"""Launcher orchestration with synthetic provider/slot evidence and no model call."""
from contextlib import ExitStack, nullcontext
from pathlib import Path
from types import SimpleNamespace
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import scheduled_operator as operator, execution_profiles, repair_execution
from do_math.configuration import DEFAULT_CONFIG
from record_fixtures import installation_repair_state


class DiagnosedRecoveryTests(unittest.TestCase):
    def run_case(self, outcome, *, runner_result=None, during_call=None, probe_exit=0):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        runtime, diagnosis = installation_repair_state()
        configured = execution_profiles.build_profiles(DEFAULT_CONFIG)
        state = {**configured, 'config':dict(DEFAULT_CONFIG), 'id':'RI-fixture'}
        repository = SimpleNamespace(git_dir=root,
            writer_lock=lambda: nullcontext(), load=lambda: ('head',state,runtime),
            read=lambda path, snapshot: b'{"preserved":"actual rejected response"}',
            save_with_state=lambda *a, **k: ('next-head', state, runtime))
        self.provider_results = Mock(return_value={})
        # The slot double keeps SessionSlots' lifecycle contract: admission moves
        # the execution to starting and the started Job to running.
        from do_math.execution_lifecycle import transition_execution
        def acquire(eid, *, profile, execution):
            from do_math.launch import ticket
            execution['launch_ticket'] = ticket(eid, profile)
            transition_execution(execution, 'starting', at='2026-09-20T00:00:00+00:00')
            return True
        def started(eid, identity, *, at):
            transition_execution(runtime['executions'][eid], 'running', at=at)
        slots = SimpleNamespace(acquire=acquire, started=started,
            release=lambda *a, **k:True, provider_result_from_run=self.provider_results)
        installation = root/'skill'
        installation.mkdir()
        (installation/'SKILL.md').write_text('fixture installation',encoding='utf-8')
        observed = []
        self.runner_results = []
        def provider(**arguments):
            observed.append(arguments)
            arguments['on_started']({'pid':123,'job_name':arguments['launch_ticket']['job_name']})
            (arguments['workspace']/'regression.txt').write_text('Synthetic regression: former input now accepted',encoding='utf-8')
            if during_call:
                during_call(root/'work')
            result = {**{'status':'completed','output':{'repair_outcome':outcome,'verification_evidence':['regression.txt'],
                'summary':'synthetic repair','observed_status':outcome,'actions':['fixture inspection'],
                'evidence_paths':['regression.txt'],'user_questions':[],'next_step':'launcher continuation'}},
                **(runner_result or {})}
            self.runner_results.append(result)
            return result
        stack = ExitStack()
        self.addCleanup(stack.close)
        for owner,name,value in (
            (operator,'ResearchRepository',repository), (operator,'LIVE_INSTALLATION_ROOT',installation),
        ):
            stack.enter_context(patch.object(owner,name,return_value=value) if name=='ResearchRepository' else patch.object(owner,name,value))
        stack.enter_context(patch('do_math.local_host.adapter_for',return_value=SimpleNamespace(capability_identity=lambda:{})))
        stack.enter_context(patch('do_math.initialization.capability_requirements',return_value={'satisfied':True}))
        stack.enter_context(patch('do_math.session_slots.SessionSlots',return_value=slots))
        stack.enter_context(patch('do_math.file_io.os_lock',return_value=nullcontext()))
        stack.enter_context(patch.object(operator,'ModelRunner',return_value=SimpleNamespace(run=provider)))
        verify = stack.enter_context(patch.object(operator.subprocess,'run',return_value=subprocess.CompletedProcess([],probe_exit,'verified','')))
        wake = stack.enter_context(patch.object(operator,'wake',return_value={'outcome':'engine_requested'}))
        arguments = (root/'repo','RI-fixture',root/'work')
        result = operator.recovery(*arguments, failure=repair_execution.installation_failure(runtime,diagnosis))
        return root,runtime,diagnosis,observed,result,verify,wake,arguments

    def test_success_restores_failed_request_after_locks_and_retains_proof(self):
        root,runtime,diagnosis,observed,result,verify,wake,_ = self.run_case('repaired')
        self.assertEqual(result['outcome'],'repaired',result)
        self.assertEqual(diagnosis['status'],'applied')
        self.assertEqual(runtime['queue'][0]['repair_attempt'],2)
        self.assertEqual(runtime['queue'][0]['continuation_of'],'EX-failed')
        self.assertTrue((Path(result['run_directory'])/'regression-evidence.json').is_file())
        self.assertIn('actual rejected response',(observed[0]['workspace']/'input/failure-0.json').read_text())
        verify.assert_called_once(); wake.assert_called_once()

    def test_recovery_model_policy_violation_pauses_future_calls(self):
        _, runtime, diagnosis, observed, result, verify, wake, args = self.run_case('unresolved',
            runner_result={'status': 'failed', 'output': None, 'error': 'wrong reported model',
                'error_kind': 'model_policy', 'reported_models': ['other-model']})
        self.assertEqual(result['outcome'], 'recovery_held')
        self.assertEqual(runtime['status'], 'paused')
        self.assertEqual(runtime['model_policy_violation'], {
            'execution_id': observed[0]['execution_id'],
            'assigned_model': observed[0]['model'], 'reported_models': ['other-model']})
        verify.assert_not_called()
        wake.assert_not_called()
        repeated = operator.recovery(*args,
            failure=repair_execution.installation_failure(runtime, diagnosis))
        self.assertEqual(repeated['outcome'], 'held')
        self.assertEqual(len(observed), 1)

    def test_unresolved_does_not_restart_or_repeat_same_failure_and_installation(self):
        _,runtime,diagnosis,observed,result,verify,wake,args = self.run_case('unresolved')
        self.assertEqual(result['outcome'],'recovery_failed')
        self.assertEqual(diagnosis['status'],'installation_repair_waiting')
        self.assertEqual(runtime['queue'],[])
        verify.assert_not_called(); wake.assert_not_called()
        repeated = operator.recovery(*args,failure=repair_execution.installation_failure(runtime,diagnosis))
        self.assertEqual(repeated['outcome'],'recovery_waiting')
        self.assertEqual(len(observed),1)

    def test_recovery_forwards_provider_limit_to_the_shared_gate(self):
        failure = {'kind': 'provider_limit', 'provider': 'codex',
                   'retry_at': None, 'evidence_ref': 'synthetic-provider.jsonl'}
        _, _, _, observed, result, verify, wake, _ = self.run_case('unresolved',
            runner_result={'status': 'failed', 'output': None, 'error': 'provider quota',
                           'error_kind': 'provider_limit', 'failure': failure})
        self.assertEqual(result['outcome'], 'recovery_provider_limited')
        # The shared gate reads the failure and response from the unaltered runner result.
        self.provider_results.assert_called_once_with(observed[0]['execution_id'], self.runner_results[0],
                                                      DEFAULT_CONFIG)
        self.assertEqual(self.runner_results[0]['failure'], failure)
        verify.assert_not_called()
        wake.assert_not_called()

    def test_a_provider_refused_or_held_call_does_not_use_up_the_one_repair(self):
        # None of these calls judged a repair, so the next supervision check calls the model again.
        refused = {'status': 'failed', 'output': None, 'error': 'provider quota', 'error_kind': 'provider_limit',
                   'failure': {'kind': 'provider_limit', 'provider': 'codex', 'retry_at': None,
                               'evidence_ref': 'synthetic-provider.jsonl'}}
        paused = {'status': 'failed', 'output': None, 'error': 'wrong reported model',
                  'error_kind': 'model_policy', 'reported_models': ['other-model']}
        stopped = {'status': 'stopped', 'output': None, 'error': 'stop requested or timeout',
                   'error_kind': 'execution_failure'}
        hold = lambda work: operator.hold(work, reason='user hold during the call')
        for name, outcome, runner_result, during_call in (
                ('provider limit', 'recovery_provider_limited', refused, None),
                ('model-policy pause', 'recovery_held', paused, None),
                ('HOLD stop', 'recovery_held', stopped, hold)):
            with self.subTest(name):
                _, runtime, diagnosis, observed, result, _, _, args = self.run_case('unresolved',
                    runner_result=runner_result, during_call=during_call)
                self.assertEqual(result['outcome'], outcome)
                # The user resolves the pause or HOLD; the slot double never closes a provider gate.
                runtime.pop('model_policy_violation', None)
                runtime['status'] = 'ready'
                operator.release(args[2])
                operator.recovery(*args, failure=repair_execution.installation_failure(runtime, diagnosis))
                self.assertEqual(len(observed), 2)

    def test_a_judged_repair_counts_once_even_when_a_hold_holds_its_result(self):
        # The model reported a repair that failed installation verification while a HOLD arrived.
        _, runtime, diagnosis, observed, result, verify, wake, args = self.run_case('repaired',
            during_call=lambda work: operator.hold(work, reason='user hold during the call'), probe_exit=1)
        self.assertEqual(result['outcome'], 'recovery_held')
        verify.assert_called_once()
        wake.assert_not_called()
        operator.release(args[2])
        repeated = operator.recovery(*args, failure=repair_execution.installation_failure(runtime, diagnosis))
        self.assertEqual(repeated, {'outcome': 'recovery_waiting',
                                    'reason': 'same failure and installation already attempted'})
        self.assertEqual(len(observed), 1)

    def test_normal_recovery_response_reaches_provider_reobservation(self):
        _, _, _, observed, result, _, _, _ = self.run_case('repaired')
        self.assertEqual(result['outcome'], 'repaired')
        self.provider_results.assert_called_once_with(observed[0]['execution_id'], self.runner_results[0],
                                                      DEFAULT_CONFIG)
        self.assertEqual(self.runner_results[0]['status'], 'completed')


if __name__ == '__main__':
    unittest.main()
