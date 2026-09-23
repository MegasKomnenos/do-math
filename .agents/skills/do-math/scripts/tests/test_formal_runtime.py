"""Lean completes without execution budgets; cancellation and evidence remain observable."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from test_categories import test_group as category
from do_math import formal
from test_formal import actual_command


class FormalRuntimeTests(unittest.TestCase):
    @category('lean')
    def test_shared_expression_evidence_does_not_expand_shared_subterms(self):
        source = ('import Lean\n' + formal._DEPENDENCY_EXTRACTOR + '\n'
                  'open Lean\nrun_elab do\n'
                  '  let mut value := mkRawNatLit 0\n'
                  '  for _ in [:20] do\n'
                  '    value := mkApp2 (mkConst ``Nat.add) value value\n'
                  '  IO.println (← DoMathDependencyAudit.exprEvidence value)\n'
                  '  let left := mkLambda `left .default (mkConst ``Nat) (mkBVar 0)\n'
                  '  let right := mkLambda `right .default (mkConst ``Nat) (mkBVar 0)\n'
                  '  IO.println (← DoMathDependencyAudit.exprEvidence (mkApp left right))\n')
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            source_path = workspace / 'sharing.lean'
            source_path.write_text(source, encoding='utf-8')
            result = formal._job_run([*actual_command(), str(source_path)], workspace)
        self.assertEqual(result[0], 0, result[1] + result[2])
        evidence, binders = map(json.loads, result[1].splitlines())
        self.assertEqual(evidence['format'], 'lean-expr-dag/1')
        self.assertLessEqual(len(evidence['nodes']), 42)
        self.assertLess(len(result[1]), 10000)
        atoms = {argument['atom'] for node in binders['nodes'] for argument in node['args'] if 'atom' in argument}
        self.assertTrue({'`left', '`right'}.issubset(atoms))
        for graph in (evidence, binders):
            for index, node in enumerate(graph['nodes']):
                for argument in node['args']:
                    if 'ref' in argument:
                        self.assertLess(argument['ref'], index)

    @category('lean')
    def test_flat_representation_preserves_literal_spaces_and_unicode_binders(self):
        source = ('def textBase : String := "a  b\\nc"\n'
                  'def identityBase (Ω : Nat) : Nat := Ω\n'
                  'def textLeaf : String := textBase\n'
                  'def functionLeaf : Nat → Nat := identityBase')
        with tempfile.TemporaryDirectory() as directory:
            result = formal.verify_lean(source=source, declarations=['textLeaf', 'functionLeaf'],
                workspace=Path(directory), lean_command=actual_command())
        self.assertEqual(result['status'], 'verified', {key:result.get(key) for key in ('reason','stderr','exit_code')})
        rows = {row['name']: row for row in
                (json.loads(line.removeprefix('__DO_MATH_DEPENDENCY__'))
                 for line in result['stdout'].splitlines() if line.startswith('__DO_MATH_DEPENDENCY__'))}
        atoms = [argument['atom'] for node in json.loads(rows['textBase']['evidence']['value'])['nodes']
                 for argument in node['args'] if 'atom' in argument]
        self.assertTrue(any('"a  b\\nc"' in atom for atom in atoms))
        self.assertIn('Ω', rows['identityBase']['evidence']['type'])

    @category('lean')
    def test_dependency_representation_does_not_expand_layout_indentation(self):
        with tempfile.TemporaryDirectory() as directory:
            result = formal.verify_lean(source='theorem good (p : Prop) : p ∨ ¬p := Classical.em p',
                declarations=['good'], workspace=Path(directory), lean_command=actual_command())
        self.assertEqual(result['status'], 'verified', {key:result.get(key) for key in ('reason','stderr','exit_code')})
        rows = [json.loads(line.removeprefix('__DO_MATH_DEPENDENCY__'))
                for line in result['stdout'].splitlines() if line.startswith('__DO_MATH_DEPENDENCY__')]
        self.assertTrue(rows)
        for row in rows:
            self.assertNotIn('\n', row['evidence']['type'], row['name'])
            self.assertNotIn('\n', row['evidence']['value'] or '', row['name'])

    def test_uncapped_lean_admission_with_an_adopted_host_budget(self):
        from do_math import execution_profiles as profiles
        from do_math.session_slots import GitSessionSlots
        from test_host_resources import fixture
        from test_redesign_PROFILES import CONFIG
        _, _, constraint = fixture()
        bare = profiles.build_profiles(CONFIG)
        demands = {p['role']: {'jobs': 1, 'memory_bytes': 128*1024**2, 'cpu_rate_basis_points': 1000}
                   for p in bare['execution_profiles'].values()}
        instance = profiles.build_profiles({**CONFIG, 'lean_command': [sys.executable],
            'host_resources': {'constraint': constraint, 'demands_by_role': demands}})
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'formal_check')
        self.assertIsNone(profiles.job_resource_limits(profile))
        invocation = profiles.machine_invocation(profile,
            trust_environment={'toolchain': {'configured_command': [sys.executable]}})
        self.assertIsNone(invocation['timeout_seconds'])
        self.assertNotIn('resource_limits', invocation)
        runtime = {'executions': {}, 'reservations': {}}
        execution = {'id': 'EX-unlimited', 'role': 'formal_check', 'status': 'queued'}
        self.assertTrue(GitSessionSlots(runtime, instance).acquire(execution['id'], profile['budget_kind'], None,
            profile=profile, execution=execution))
        self.assertEqual(runtime['reservations'], {})

    @category('resource')
    def test_output_larger_than_the_discarded_cap_is_preserved(self):
        count = 33 * 1024 * 1024
        with tempfile.TemporaryDirectory() as directory:
            result = formal._job_run([sys.executable, '-c',
                f"import sys; sys.stdout.write('x'*{count})"], Path(directory))
        self.assertEqual(result[0], 0)
        self.assertEqual(len(result[1]), count)

    def test_legacy_timeout_does_not_interrupt_work(self):
        with tempfile.TemporaryDirectory() as directory:
            result = formal._job_run([sys.executable, '-c',
                "import time; time.sleep(.25); print('completed')"], Path(directory), .01)
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1].strip(), 'completed')
        self.assertFalse(result[3])

    def test_formal_verification_does_not_apply_memory_or_cpu_caps(self):
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(formal, 'inspect_toolchain', return_value={}), \
                patch.object(formal, '_job_run', return_value=(1, '', 'fixture', False, False)) as run:
            formal.verify_lean(source='', declarations=['good'], workspace=Path(directory),
                lean_command=[sys.executable], resource_limits={'memory_bytes': 1, 'cpu_rate_basis_points': 1})
        self.assertIsNone(run.call_args.kwargs.get('resource_limits'))

    @category('lean')
    def test_common_dependency_bodies_are_emitted_once(self):
        with tempfile.TemporaryDirectory() as directory:
            result = formal.verify_lean(source='theorem first : True := True.intro\n'
                'theorem second : True := True.intro', declarations=['first', 'second'],
                workspace=Path(directory), lean_command=actual_command())
        self.assertEqual(result['status'], 'verified', {key:result.get(key) for key in ('reason','stderr','exit_code')})
        rows = [json.loads(line.removeprefix('__DO_MATH_DEPENDENCY__'))
                for line in result['stdout'].splitlines() if line.startswith('__DO_MATH_DEPENDENCY__')]
        self.assertEqual({row['name'] for row in rows}, {'True', 'True.intro'})
        self.assertEqual(len(rows), 2)
        self.assertEqual(result['dependency_evidence']['first'], result['dependency_evidence']['second'])


if __name__ == '__main__':
    unittest.main()
