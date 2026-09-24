"""Launcher orchestration with synthetic provider/slot evidence and no model call."""
from contextlib import ExitStack, nullcontext
from pathlib import Path
from types import SimpleNamespace
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import scheduled_operator as operator, execution_profiles, repair_execution
from do_math.engine import DEFAULT_CONFIG
import test_walkthrough_contract_repairs as fixtures


class DiagnosedRecoveryTests(unittest.TestCase):
    def run_case(self, outcome):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        runtime, diagnosis = fixtures.WalkthroughRepairs().installation_fixture()
        configured = execution_profiles.build_profiles(DEFAULT_CONFIG)
        profile = next(p for p in configured['execution_profiles'].values() if p['role'] == 'recovery')
        state = {**configured, 'config':{'operator_enabled':True}, 'id':'RI-fixture'}
        repository = SimpleNamespace(_store=SimpleNamespace(_git_dir=root),
            writer_lock=lambda: nullcontext(), load=lambda: ('head',state,runtime),
            read=lambda path, snapshot: b'{"preserved":"actual rejected response"}',
            save=lambda *a, **k: 'next-head')
        slots = SimpleNamespace(acquire=lambda *a, **k:True, started=lambda *a, **k:None, release=lambda *a:True)
        installation = root/'skill'
        installation.mkdir()
        (installation/'SKILL.md').write_text('fixture installation',encoding='utf-8')
        observed = []
        def provider(**arguments):
            observed.append(arguments)
            arguments['on_started']({'pid':123,'job_name':'synthetic-not-a-real-process'})
            (arguments['workspace']/'regression.txt').write_text('Synthetic regression: former input now accepted',encoding='utf-8')
            return {'status':'completed','output':{'repair_outcome':outcome,'verification_evidence':['regression.txt'],
                'summary':'synthetic repair','observed_status':outcome,'actions':['fixture inspection'],
                'evidence_paths':['regression.txt'],'user_questions':[],'next_step':'launcher continuation'}}
        stack = ExitStack()
        self.addCleanup(stack.close)
        for owner,name,value in (
            (operator,'ResearchRepository',repository), (operator,'LIVE_INSTALLATION_ROOT',installation),
        ):
            stack.enter_context(patch.object(owner,name,return_value=value) if name=='ResearchRepository' else patch.object(owner,name,value))
        stack.enter_context(patch.object(operator,'register_profile_families'))
        stack.enter_context(patch.object(operator,'selection',return_value={'model':profile['ai']['model']}))
        stack.enter_context(patch('do_math.execution_profiles.select_profile',return_value=profile))
        stack.enter_context(patch('do_math.initialization.adapter_for',return_value=SimpleNamespace(capability_identity=lambda:{})))
        stack.enter_context(patch('do_math.initialization.capability_requirements',return_value={'satisfied':True}))
        stack.enter_context(patch('do_math.session_slots.SessionSlots',return_value=slots))
        stack.enter_context(patch('do_math.session_slots._lock',return_value=object()))
        stack.enter_context(patch('do_math.session_slots._unlock'))
        stack.enter_context(patch.object(operator,'ModelRunner',return_value=SimpleNamespace(run=provider)))
        verify = stack.enter_context(patch.object(operator.subprocess,'run',return_value=subprocess.CompletedProcess([],0,'verified','')))
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

    def test_unresolved_does_not_restart_or_repeat_same_failure_and_installation(self):
        _,runtime,diagnosis,observed,result,verify,wake,args = self.run_case('unresolved')
        self.assertEqual(result['outcome'],'recovery_failed')
        self.assertEqual(diagnosis['status'],'installation_repair_waiting')
        self.assertEqual(runtime['queue'],[])
        verify.assert_not_called(); wake.assert_not_called()
        repeated = operator.recovery(*args,failure=repair_execution.installation_failure(runtime,diagnosis))
        self.assertEqual(repeated['outcome'],'recovery_waiting')
        self.assertEqual(len(observed),1)

    def test_report_without_real_regression_file_cannot_claim_repaired(self):
        with tempfile.TemporaryDirectory() as directory:
            for output in ({'repair_outcome':'repaired','verification_evidence':[]},
                           {'repair_outcome':'repaired','verification_evidence':['missing.txt']},
                           {'repair_outcome':'unresolved','verification_evidence':['missing.txt']}):
                with self.assertRaises(ValueError):
                    operator.collect_repair_verification(output,Path(directory))


if __name__ == '__main__':
    unittest.main()
