"""10-A 녹화 5선언·603폐포를 실제 verifier→worker→저장→검토 입력으로 잇는다.

실측 원 시험1.469초. 실제 작업자·저장·다섯 검토 단계를 포함해 flows에 둔다.
사전 검사1MB·파일 회수4096바이트 상한과 원천 대비 형식 기록 상한을 따로 검사한다.
"""
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from do_math import formal, formal_preview, knowledge_io, knowledge_records, input_tool, submission, contracts
from do_math.canonical import canonical_json, exact_content_hash
from do_math.context_store import prepare_role_input
from do_math.lean_evidence import check_file
from do_math.review_cycle import review_proposal
from do_math import review_cycle
from support.review_inputs import review_stage_output
from support.role_answers import scope_response
from support.engine_lean_recording import DECLARATIONS, RAW_BYTES, RAW_SHA256, SOURCE, recorded_stdout
from support.knowledge_builders import knowledge_candidate
from support.knowledge_verifier_jobs import OutputCompiler, worker_jobs
from support.sim import Sim, warm_template
from support.engine_tool_output import invoke_tool
from support.engine_size_cases import assert_input_budget
from support.role_input_requirements import assert_judgment_inputs


setUpModule = warm_template


class BoundRecordingCompiler(OutputCompiler):
    """원천·선언·중앙 검사 파일이 녹화와 같은 요청일 때만 원문을 재생한다."""
    def __init__(self, stdout, *, extract_evidence=True, declarations=DECLARATIONS):
        super().__init__(stdout)
        self.extract_evidence = extract_evidence
        self.declarations = declarations

    def __call__(self, command, **options):
        requested = Path(command[-1]).read_bytes()
        expected = check_file(SOURCE.encode('utf-8'), list(self.declarations), extract_evidence=self.extract_evidence)
        if requested != expected:
            raise AssertionError('녹화와 다른 Lean 원천 또는 선언 요청')
        return super().__call__(command, **options)


class RecordedLeanScaleTests(unittest.TestCase):
    def test_preview_is_one_bounded_json_and_full_recording_is_readable_as_output_file(self):
        sim = Sim.activated()
        raw = recorded_stdout()
        preview_stdout = ''.join(line for line in raw.decode('utf-8').splitlines(keepends=True)
                                 if not line.startswith('__DO_MATH_DEPENDENCY__'))
        compiler = BoundRecordingCompiler(preview_stdout, extract_evidence=False)
        ports = replace(sim.ports, jobs=worker_jobs(compiler))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'proof.lean').write_bytes(SOURCE.encode('utf-8'))
            context = sim.engine._context({'id': 'AC-preview', 'role': 'maintenance'}, root)
            submission.install_tools(root, context, contracts.schema_for('maintenance'), None, clock=sim.clock)
            args = ['--source', 'proof.lean', *[part for name in DECLARATIONS for part in ('--declaration', name)]]
            code, output = invoke_tool(formal_preview.main, root, args, ports=ports, environment=sim.environment)
            value = json.loads(output)
            self.assertEqual((code, value['status'], value['authoritative']), (0, 'verified', False))
            self.assertEqual(value['declarations'], list(DECLARATIONS))
            self.assertEqual(value['source_sha256'], hashlib.sha256(SOURCE.encode()).hexdigest())
            self.assertEqual(value['stdout'], preview_stdout)
            self.assertEqual(value['stderr'], '')
            # identity_errors는 식별 불일치 결과에만 존재한다(formal.verify_lean).
            self.assertEqual(set(value), set(formal_preview.PREVIEW_FIELDS) - {'identity_errors'})
            # 조사 C-10의 1MB 잘림 경계보다 작아야 JSON 하나를 운전 도구가 회수한다.
            self.assertLessEqual(len(output), 1_000_000)
            self.assertEqual(len(compiler.commands), 1)
            self.assertTrue(ports.jobs.launched[0].closed)
            artifact = 'runtime/artifacts/BA-engine-size/recorded-lean.txt'
            sim.engine._save(artifacts={artifact: raw})
            root = root / 'reader'
            root.mkdir()
            context = sim.engine._context({'id': 'AC-read', 'role': 'maintenance'}, root)
            profile = sim.instance['execution_profiles'][sim.instance['role_profile_refs']['maintenance'][0]['id']]
            prepared = prepare_role_input(context, instance=sim.instance, runtime=sim.runtime,
                role='maintenance', profile=profile, snapshot=sim.engine.head, workspace=root,
                activity_id='AC-read', clock=sim.clock)
            submission.install_tools(root, prepared['validation_context'], contracts.schema_for('maintenance'), None, clock=sim.clock)
            code, output = invoke_tool(input_tool.read_main, root, ['--path', artifact, '--output', 'read/full.txt'],
                                      ports=sim.ports, environment=sim.environment)
            value = json.loads(output)
            self.assertEqual((code, value['status']), (0, 'ok'), value)
            self.assertEqual((root / 'read/full.txt').read_bytes(), raw)
            self.assertEqual((value['records'][0]['bytes'], value['records'][0]['sha256']), (RAW_BYTES, RAW_SHA256))
            self.assertLessEqual(len(output), 4096)

    def test_full_recording_is_reduced_once_and_published_without_inline_dependency_bodies(self):
        raw = recorded_stdout()
        self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()), (RAW_BYTES, RAW_SHA256))
        dependencies = [json.loads(line.removeprefix('__DO_MATH_DEPENDENCY__'))
                        for line in raw.decode('utf-8').splitlines()
                        if line.startswith('__DO_MATH_DEPENDENCY__')]
        self.assertEqual(len(dependencies), 603)
        self.assertEqual(len(DECLARATIONS), 5)
        expected_hashes = {row['name']: exact_content_hash(row['evidence']) for row in dependencies}
        sim = Sim.activated()
        environment_id = sim.instance['active_trust_environment']
        environment = sim.instance['trust_environments'][environment_id]
        compiler = BoundRecordingCompiler(raw.decode('utf-8'))
        jobs = worker_jobs(compiler)
        with tempfile.TemporaryDirectory() as directory:
            result = formal.verify_lean(source=SOURCE, declarations=list(DECLARATIONS), workspace=Path(directory),
                lean_command=sim.instance['config']['lean_command'], expected_toolchain=environment['toolchain'],
                allowed_axioms=tuple(environment['allowed_axioms']), jobs=jobs, clock=sim.clock,
                environment=sim.environment, git_backend=sim.ports.git_backend)
        self.assertEqual((result['status'], result['reason']), ('verified', None))
        self.assertEqual(result['dependency_evidence'], expected_hashes)
        self.assertEqual({name: len(refs) for name, refs in result['dependency_closure'].items()},
                         {name: 71 if name == 'natAddZeroBeqGoal' else 603 for name in DECLARATIONS})
        self.assertEqual(len(compiler.commands), 1)
        self.assertEqual(len(jobs.launched), 1)
        self.assertTrue(jobs.launched[0].closed)
        self.assertNotIn('__DO_MATH_DEPENDENCY__', result['stdout'])
        expected_stdout = ''.join(line for line in raw.decode('utf-8').splitlines(keepends=True)
                                  if not line.startswith('__DO_MATH_DEPENDENCY__'))
        self.assertEqual(result['stdout'], expected_stdout)
        candidate = knowledge_candidate(lean_code=SOURCE, declaration_names=list(DECLARATIONS))
        instance, runtime, kid = knowledge_io.import_candidate(sim.instance, sim.runtime, candidate,
            source_ref='engine:실제 녹화 재생', actor_ref='engine:규모 시험', clock=sim.clock)
        sim.engine.instance = knowledge_records.record_formal_result(instance, kid, result, environment_id, runtime=runtime)
        sim.engine.runtime = runtime
        sim.engine._save()
        _, stored, _ = sim.engine.store.load()
        formal_record = stored['formal_results'][stored['knowledge'][kid]['formal_result_id']]
        self.assertEqual(formal_record['verification'], result)
        self.assertEqual(formal_record['lean_code'], SOURCE)
        self.assertEqual(formal_record['declaration_names'], list(DECLARATIONS))
        # 의존 본문 전건은 해시표 하나로 대체된다. 현재 결과 길이에 맞춘 상수는 쓰지 않는다.
        logical = canonical_json(formal_record)
        self.assertLessEqual(len(logical), len(raw) + len(SOURCE.encode('utf-8')) + 4096)
        for row in dependencies:
            value = row['evidence'].get('value')
            if value and len(value) > 10000:
                self.assertNotIn(canonical_json(value).strip(), logical)
        proposal = review_proposal(stored, kid)
        self.assertNotIn('stdout', proposal['formal'])
        self.assertNotIn('dependency_evidence', proposal['formal'])
        for role, direct in [('identity_review', {'role_review': {'proposal': proposal}}),
                             ('goal_audit', {'eligible_knowledge': [knowledge_records.proposal_view(stored, kid)]})]:
            with self.subTest(role=role), tempfile.TemporaryDirectory() as directory:
                profile = next(p for p in stored['execution_profiles'].values() if p['role'] == role)
                packaged = prepare_role_input({'action': {'id': 'AC-recorded', 'role': role}, **deepcopy(direct)},
                    instance=stored, runtime=runtime, role=role, profile=profile, snapshot=sim.engine.head,
                    workspace=Path(directory), activity_id='AC-recorded', clock=sim.clock)
                self.assertIsNone(packaged['overflow'], packaged['overflow'])
                self.assertLessEqual(len(packaged['prompt'].encode('utf-8')), profile['input']['max_input_bytes'])
                self.assertNotIn('__DO_MATH_DEPENDENCY__', packaged['prompt'])
                self.assertEqual({key: packaged['context'][key] for key in direct}, direct)
        # 실제 cycle 생산자·수신자로 모든 검토 단계를 만들고 자리별 입력을 포장한다.
        cycle_id = sim.engine._start_identity_review(kid)
        cycle = deepcopy(sim.runtime['review_cycles'][cycle_id])
        profile = next(p for p in stored['execution_profiles'].values() if p['role'] == 'identity_review')
        visited = []
        for number in range(20):
            pending = review_cycle.next_actions(cycle)
            if not pending:
                break
            selected = pending[0]
            stage = selected['stage']
            visited.append(stage)
            action = {'id': f'AC-review-size-{number}', 'role': 'identity_review',
                      'target': kid, 'review_cycle_id': cycle_id, **selected}
            direct = review_cycle.context_for(cycle, selected)
            with tempfile.TemporaryDirectory() as directory:
                packaged = prepare_role_input({'action': action, 'role_review': direct},
                    instance=stored, runtime={**sim.runtime, 'review_cycles': {cycle_id: cycle}},
                    role='identity_review', profile=profile, snapshot=sim.engine.head,
                    workspace=Path(directory), activity_id=action['id'], clock=sim.clock)
                self.assertIsNone(packaged['overflow'], packaged['overflow'])
                self.assertLessEqual(packaged['actual_bytes'], profile['input']['max_input_bytes'])
                self.assertEqual(packaged['manifest']['private_scope']['view_sha256'], exact_content_hash(direct))
                self.assertEqual(packaged['validation_context']['role_review'], direct)
                assert_input_budget(self, packaged, 'identity_review', profile)
                assert_judgment_inputs(self, 'identity_review', packaged, Path(directory),
                    producer_context={'action': action, 'role_review': direct})
            if stage == 'scope':
                output = {'summary': '범위 검토', 'questions': [], 'used_sources': [],
                          **scope_response({'role_review': direct, 'execution_profile': profile})}
            elif stage == 'initial':
                output = review_stage_output(cycle, stage, decision='mismatch', findings=[{
                    'id': 'finding-' + selected['slot'], 'statement': '경계 해설을 독립 검토한다.',
                    'evidence': ['proposal:1']}])
            else:
                output = review_stage_output(cycle, stage)
                if stage == 'judge' and selected['round'] == 1 and selected['slot'] == cycle['judge_slots'][0]:
                    output['decision'] = 'match'
                    for verdict in output['issue_verdicts']:
                        verdict['decision'] = 'rejected'
            cycle = review_cycle.accept_result(cycle, selected, output, f'EX-size-review-{number}')
        self.assertEqual(set(visited), {'scope', 'initial', 'organize', 'answer', 'judge'})
        self.assertEqual(review_cycle.next_actions(cycle), [])
        # Keep the full five-declaration recording above. A derived one-declaration
        # replay holds the shared 603-body closure fixed while changing declaration count.
        # It is a projection of the recording, not a second external Lean measurement.
        name = DECLARATIONS[-1]
        selected = []
        signature = None
        for line in raw.decode('utf-8').splitlines(keepends=True):
            if line.strip().startswith('"__DO_MATH_SIGNATURE_BEGIN_'):
                signature = next(declaration for declaration in DECLARATIONS
                    if line.strip() == '"__DO_MATH_SIGNATURE_BEGIN_' + declaration + '__"')
            keep = signature is None or signature == name
            if line.startswith('__DO_MATH_DEPENDENCIES__'):
                keep = json.loads(line.removeprefix('__DO_MATH_DEPENDENCIES__'))['declaration'] == name
            if any(line.startswith("'" + declaration + "'") for declaration in DECLARATIONS if declaration != name):
                keep = False
            if keep:
                selected.append(line)
            if signature and line.strip() == '"__DO_MATH_SIGNATURE_END_' + signature + '__"':
                signature = None
        one_stdout = ''.join(selected)
        self.assertEqual(sum(line.startswith('__DO_MATH_DEPENDENCY__')
            for line in one_stdout.splitlines()), 603)
        compiler = BoundRecordingCompiler(one_stdout, declarations=(name,))
        jobs = worker_jobs(compiler)
        with tempfile.TemporaryDirectory() as directory:
            one = formal.verify_lean(source=SOURCE, declarations=[name], workspace=Path(directory),
                lean_command=sim.instance['config']['lean_command'], expected_toolchain=environment['toolchain'],
                allowed_axioms=tuple(environment['allowed_axioms']), jobs=jobs, clock=sim.clock,
                environment=sim.environment, git_backend=sim.ports.git_backend)
        self.assertEqual((one['status'], one['reason']), ('verified', None))
        self.assertEqual(one['dependency_evidence'], expected_hashes)
        self.assertEqual(one['dependency_closure'], {name: result['dependency_closure'][name]})
        self.assertEqual(len(compiler.commands), 1)
        self.assertTrue(jobs.launched[0].closed)
        candidate = knowledge_candidate(lean_code=SOURCE, declaration_names=[name])
        instance, runtime, one_kid = knowledge_io.import_candidate(sim.instance, sim.runtime, candidate,
            source_ref='engine:녹화의 1선언 투영', actor_ref='engine:규모 시험', clock=sim.clock)
        sim.engine.instance = knowledge_records.record_formal_result(instance, one_kid, one, environment_id, runtime=runtime)
        sim.engine.runtime = runtime
        sim.engine._save()
        _, stored_one, _ = sim.engine.store.load()
        one_record = stored_one['formal_results'][stored_one['knowledge'][one_kid]['formal_result_id']]
        self.assertEqual(one_record['verification'], one)
        # Shared hashes are charged once; the remaining record grows with declarations.
        shared_bytes = len(canonical_json(expected_hashes))
        one_variable = len(canonical_json(one_record)) - shared_bytes - len(SOURCE.encode('utf-8'))
        five_variable = len(logical) - shared_bytes - len(SOURCE.encode('utf-8'))
        self.assertLessEqual(five_variable, len(DECLARATIONS) * one_variable + 4096)
