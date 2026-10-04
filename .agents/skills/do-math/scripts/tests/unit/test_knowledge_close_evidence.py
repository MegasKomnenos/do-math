"""정상 생산 합성 출력의 한 행·필드 변조와 1층 판정 함수의 정확한 결과."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from do_math import lean_evidence as le
from do_math.canonical import exact_content_hash
from support.knowledge_close_inputs import NAME, SOURCE, compiler_output, parse_base
from support.trust_inputs import trust_fixture




class EvidenceGuards(unittest.TestCase):
    def setUp(self):
        self.stdout = compiler_output()

    def changed_row(self, prefix, change):
        lines = self.stdout.splitlines(keepends=True)
        for index, line in enumerate(lines):
            if line.startswith(prefix):
                row = json.loads(line[len(prefix):])
                change(row)
                lines[index] = prefix + json.dumps(row) + '\n'
                break
        else:
            self.fail('생산자 출력에 대상 행 없음')
        return ''.join(lines)

    def test_normal_output_reduces_bodies_and_keeps_exact_hashes(self):
        result = le.parse_evidence(parse_base(self.stdout), [NAME], [])
        self.assertEqual((result['status'], result['reason']), ('verified', None))
        self.assertEqual(result['dependency_closure'], {NAME: ['True']})
        self.assertEqual(result['dependency_evidence'], {'True': exact_content_hash({'type': 'Prop', 'value': None})})
        self.assertEqual(result['declaration_evidence'], {NAME: {'type': 'True', 'value': None}})
        self.assertEqual(result['declaration_signatures'], {NAME: NAME + ' : True'})
        self.assertEqual(result['stdout'], ''.join(line for line in self.stdout.splitlines(keepends=True)
            if not line.startswith('__DO_MATH_DEPENDENCY__')))

    def test_dependency_row_rejects_invalid_name_type_and_value(self):
        for field, value in (('name', 1), ('evidence', []), ('evidence', {'type': 1}),
                             ('evidence', {'type': 'Prop', 'value': []})):
            with self.subTest(field=field, value=value):
                output = self.changed_row('__DO_MATH_DEPENDENCY__', lambda row: row.update({field: value}))
                result = le.parse_evidence(parse_base(output), [NAME], [])
                self.assertEqual((result['status'], result['reason']), ('failed', 'malformed dependency evidence'))

    def test_duplicate_dependency_and_declaration_rows_are_rejected(self):
        for prefix in ('__DO_MATH_DEPENDENCY__', '__DO_MATH_DEPENDENCIES__'):
            with self.subTest(prefix=prefix):
                line = next(line for line in self.stdout.splitlines(keepends=True) if line.startswith(prefix))
                result = le.parse_evidence(parse_base(self.stdout + line), [NAME], [])
                self.assertEqual((result['status'], result['reason']), ('failed', 'malformed dependency evidence'))

    def test_declaration_row_rejects_foreign_names_and_invalid_fields(self):
        for field, value in (('declaration', 'other'), ('dependencies', {}), ('dependencies', [1]),
                             ('evidence', []), ('evidence', {'type': 1}), ('axioms', {}), ('axioms', [1])):
            with self.subTest(field=field, value=value):
                output = self.changed_row('__DO_MATH_DEPENDENCIES__', lambda row: row.update({field: value}))
                result = le.parse_evidence(parse_base(output), [NAME], [])
                self.assertEqual((result['status'], result['reason']), ('failed', 'malformed dependency evidence'))


    def test_axiom_extraction_must_match_printed_axioms(self):
        output = self.changed_row('__DO_MATH_DEPENDENCIES__', lambda row: row.update(axioms=['propext']))
        result = le.parse_evidence(parse_base(output), [NAME], le.AXIOMS)
        self.assertEqual((result['status'], result['reason']), ('failed', 'axiom extraction mismatch'))

    def test_missing_dependency_body_is_not_an_empty_closure(self):
        output = ''.join(line for line in self.stdout.splitlines(keepends=True) if not line.startswith('__DO_MATH_DEPENDENCY__'))
        result = le.parse_evidence(parse_base(output), [NAME], [])
        self.assertEqual((result['status'], result['reason']), ('failed', 'dependency output missing'))

    def test_malformed_axiom_output_is_not_accepted(self):
        output = self.stdout.replace("does not depend on any axioms", 'depends on invalid')
        result = le.parse_evidence(parse_base(output), [NAME], [])
        self.assertEqual((result['status'], result['reason']), ('failed', 'malformed axiom output'))

    def test_preview_requires_signature_and_axiom_rows(self):
        for removed, reason in ((NAME + ' : True\n', 'signature output missing'),
                                ("'" + NAME + "' does not depend on any axioms\n", 'axiom output missing')):
            with self.subTest(reason=reason):
                result = le.parse_evidence(parse_base(self.stdout.replace(removed, '')), [NAME], [], extract_evidence=False)
                self.assertEqual((result['status'], result['reason']), ('failed', reason))

    def test_sorry_is_never_allowed(self):
        self.assertEqual(le.forbidden_axioms({NAME: ['sorryAx', 'propext']}, ['sorryAx', 'propext']), {'sorryAx'})
        output = self.stdout.replace('does not depend on any axioms', 'depends on axioms: [sorryAx]')
        result = le.parse_evidence(parse_base(output), [NAME], ['sorryAx'])
        self.assertEqual((result['status'], result['reason']), ('rejected', 'forbidden axiom'))

    def test_stop_prevents_parsing(self):
        base = parse_base(self.stdout)
        before = deepcopy(base)
        with self.assertRaisesRegex(le.VerificationStopped, '^verification stopped$'):
            le.parse_evidence(base, [NAME], [], lambda: True)
        self.assertEqual(base, before)

    def test_comparison_reports_missing_and_changed_fields_in_contract_order(self):
        result = le.parse_evidence(parse_base(self.stdout), [NAME], [])
        current = deepcopy(result)
        current.pop('dependency_evidence')
        current['axioms'] = {NAME: ['propext']}
        self.assertEqual(le.compare_formal_results(result, current), {'equivalent': False,
            'missing': ['dependency_evidence'], 'changed': ['axioms'], 'requires_identity_review': True})

    def test_toolchain_shape_rejections_are_precise(self):
        with tempfile.TemporaryDirectory() as directory:
            toolchain = trust_fixture(Path(directory), ['synthetic-lean'])['toolchain']
            self.assertEqual(le.toolchain_errors(toolchain), [])
            for field, value, reason in (('version', '', 'toolchain.version must be nonempty'),
                    ('sha256', 'bad', 'toolchain.sha256 must be a SHA-256'),
                    ('version_exit', True, 'toolchain.version_exit must record a successful version observation'),
                    ('executables', [], 'toolchain.executables must map paths to SHA-256 values'),
                    ('project', {}, 'toolchain.project must be null or the observed Lake project identity'),
                    ('configured_command', ['bad\x00'], 'toolchain.configured_command must be a nonempty argv')):
                with self.subTest(field=field):
                    self.assertEqual(le.toolchain_errors({**toolchain, field: value}), [reason])
        self.assertEqual(le.toolchain_errors(False), ['toolchain must be an object'])

    def test_os_error_completion_shape(self):
        error = dict(errno=2, strerror='missing', filename='file', winerror=None, filename2=None, message='missing')
        valid = dict(state='worker_error', exit=None, os_error=error)
        self.assertIsNone(le.check_completion_status(valid))
        for field, value in (('errno', True), ('message', None), ('filename2', 2)):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, '^invalid completion OS error$'):
                le.check_completion_status({**valid, 'os_error': {**error, field: value}})
        with self.assertRaisesRegex(ValueError, '^invalid completion status$'):
            le.check_completion_status({'state': 'exited', 'exit': True})

    def test_lake_environment_and_search_path_guards(self):
        with self.assertRaisesRegex(ValueError, '^Lake --dir requires a project path$'):
            le.lake_project_dir(['lake', '--dir'])
        for workspace, command in ((None, ['lake', 'env']), ('work', ['lake'])):
            with self.subTest(workspace=workspace), self.assertRaisesRegex(ValueError, '^Lake environment observation requires env and an observation workspace$'):
                le.lake_env_prefix(command, workspace)
        self.assertEqual(le.lake_env_prefix(['lake', '--dir', 'project', 'env', 'lean'], 'work'), ['lake', '--dir', 'project', 'env'])
        with self.assertRaisesRegex(ValueError, '^invalid project environment observation$'):
            le.check_search_path_observation({'cwd': 'work', 'paths': [1]})

    def test_commands_and_failure_reason_return_exact_verdicts(self):
        for command in ([], [''], ['lean', '\x00']):
            with self.subTest(command=command), self.assertRaisesRegex(ValueError, '^a nonempty Lean command is required$'):
                le.check_lean_command(command)
        self.assertEqual(le.command_verdict(['lean', 1]), ('rejected', 'unsafe command'))
        self.assertEqual(le.declaration_rejection([]), 'no declaration to audit')
        self.assertEqual(le.declaration_rejection(['bad;']), 'invalid declaration')
        self.assertEqual(le.compiler_failure_reason(0xC0000005, 'nt'), 'compiler crashed')
        self.assertEqual(le.compiler_failure_reason(-9, 'posix'), 'compiler crashed')
        self.assertEqual(le.compiler_failure_reason(1, 'nt'), 'lean rejected')
        self.assertEqual(le.identity_rejection_reason(['approved project inputs changed']), 'approved project inputs changed before execution')
        self.assertEqual(le.identity_rejection_reason(['other']), 'approved toolchain changed before execution')

    def test_empty_and_nontext_identifiers_and_toolchain_paths(self):
        for value in ('', None, 1):
            self.assertFalse(le.is_lean_identifier(value))
        root = Path('owned-root')
        self.assertEqual(le.portable_bin(root), root / ('lean-' + le.LEAN_VERSION) / ('lean-' + le.LEAN_VERSION + '-windows') / 'bin')
        self.assertEqual(le.mathlib_project(root), root / ('mathlib-' + le.LEAN_VERSION))
        self.assertEqual(le.command_verdict([]), ('unavailable', 'lean not found'))

    def test_project_search_paths_must_be_absolute(self):
        with tempfile.TemporaryDirectory() as directory:
            toolchain = trust_fixture(Path(directory), ['synthetic-lean'])['toolchain']
            toolchain['project'] = {'manifest_hashes': {}, 'source_identity': {'root': str(Path(directory).resolve())}, 'search_paths': ['relative']}
            self.assertEqual(le.toolchain_errors(toolchain), ['toolchain project search paths must be observed absolute paths'])

    def test_unselected_axiom_rows_do_not_enter_selected_evidence(self):
        result = le.parse_evidence(parse_base(self.stdout + "'other' depends on axioms: [sorryAx]\n"), [NAME], [])
        self.assertEqual((result['status'], result['axioms']), ('verified', {NAME: []}))
