"""Actual Lean evidence and Windows Job completion, moved from test_formal_runtime."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

from do_math import formal, lean_evidence
from provider_fixtures import actual_command
from test_categories import test_group as category

def _dependency_rows(source, declarations):
    """The dependency body rows of the central check file, which the verifier reduces to hashes."""
    with tempfile.TemporaryDirectory() as directory:
        workspace = Path(directory)
        check = workspace / 'check.lean'
        check.write_bytes(formal._check_file(source.encode(), declarations, extract_evidence=True))
        code, stdout, stderr, _ = formal._job_run([*actual_command(), str(check)], workspace)
    if code != 0:
        raise AssertionError(stdout + stderr)
    return [json.loads(line.removeprefix('__DO_MATH_DEPENDENCY__'))
        for line in stdout.splitlines() if line.startswith('__DO_MATH_DEPENDENCY__')]


class FormalRuntimeTests(unittest.TestCase):
    @category('lean')
    def test_shared_expression_evidence_does_not_expand_shared_subterms(self):
        source = ('import Lean\n' + lean_evidence.DEPENDENCY_EXTRACTOR + '\n'
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
        rows = {row['name']: row for row in _dependency_rows(source, ['textLeaf', 'functionLeaf'])}
        atoms = [argument['atom'] for node in json.loads(rows['textBase']['evidence']['value'])['nodes']
                 for argument in node['args'] if 'atom' in argument]
        self.assertTrue(any('"a  b\\nc"' in atom for atom in atoms))
        self.assertIn('Ω', rows['identityBase']['evidence']['type'])

    @category('lean')
    def test_dependency_representation_does_not_expand_layout_indentation(self):
        rows = _dependency_rows('theorem good (p : Prop) : p ∨ ¬p := Classical.em p', ['good'])
        self.assertTrue(rows)
        for row in rows:
            self.assertNotIn('\n', row['evidence']['type'], row['name'])
            self.assertNotIn('\n', row['evidence']['value'] or '', row['name'])

    @category('resource')
    def test_output_larger_than_the_discarded_cap_is_preserved(self):
        count = 33 * 1024 * 1024
        with tempfile.TemporaryDirectory() as directory:
            result = formal._job_run([sys.executable, '-c',
                f"import sys; sys.stdout.write('x'*{count})"], Path(directory))
        self.assertEqual(result[0], 0)
        self.assertEqual(len(result[1]), count)

    @category('resource')
    def test_formal_job_completes_without_deadline(self):
        with tempfile.TemporaryDirectory() as directory:
            result = formal._job_run([sys.executable, '-c',
                "import time; time.sleep(.25); print('completed')"], Path(directory))
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1].strip(), 'completed')

    @category('lean')
    def test_common_dependency_bodies_are_emitted_once(self):
        rows = _dependency_rows('theorem first : True := True.intro\ntheorem second : True := True.intro',
                                ['first', 'second'])
        self.assertEqual({row['name'] for row in rows}, {'True', 'True.intro'})
        self.assertEqual(len(rows), 2)
