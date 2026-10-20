"""13-A §6 조건부 여정: 정상 생산한 대기에서 공개 CLI로 이어간다.

초기 대기는 공통 Sim의 실제 해석·독립 검사로 만든다. 이어지는 요청·조회·
승인에는 공개 CLI의 반환만 사용하며 저장 레코드와 해시를 조립하지 않는다.
"""
from copy import deepcopy
from contextlib import redirect_stdout
from dataclasses import replace
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from do_math.configuration import DEFAULT_CONFIG
from support.engine_cli_journey import Journey
from support.governance_sim import initial_checked_sim, initial_sim, interpreted
from support.engine_overflow import overflowed_sim, held
from support.sim import Sim
from support.model import Answer
from support.fakes.scheduler import FakeScheduler


class ConditionalCliJourneyTests(unittest.TestCase):
    def test_initial_maintenance_only_grant_keeps_interpretation_pending_without_a_model_call(self):
        from datetime import timedelta
        from support.scheduling_initial import GRANT, adopted_sim
        sim = adopted_sim()
        with tempfile.TemporaryDirectory() as directory:
            journey = Journey(sim, Path(directory))
            before = deepcopy(journey.state())
            initial = next(row for row in before[2]['queue'] if row['role'] == 'intent_interpretation')
            journey.decision('revoke-initial', {'kind': 'revoke', 'grant_id': GRANT})
            journey.decision('maintenance-only', {'kind': 'grant', 'grant': {
                'id': 'GR-maintenance-only', 'kind': 'local', 'roles': ['maintenance'],
                'reuse': 'reusable', 'expires_at': (sim.clock.wall() + timedelta(days=1)).isoformat()}})
            journey.decision('adopt-narrow', {'kind': 'initialization', 'operation': 'adopt',
                'initial_grant_ids': ['GR-maintenance-only']})
            journey.call('run', '--until-active')
            _, instance, runtime = journey.state()
            self.assertEqual(instance['lifecycle']['immutable_input'], before[1]['lifecycle']['immutable_input'])
            self.assertEqual(instance['lifecycle']['state'], 'initializing')
            self.assertEqual(sim.model.calls, [])
            self.assertEqual([row for row in runtime['executions'].values() if row['actor_kind'] == 'ai'], [])
            pending, = [row for row in runtime['queue'] if row['id'] == initial['id']]
            self.assertEqual(pending['target'], initial['target'])
            self.assertEqual(pending['dispatch_wait'], {'kind': 'lifecycle',
                'reason': 'initial operating authority: no current grant permits this action'})
            self.assertEqual(instance['grants'][GRANT]['status'], 'revoked')
            self.assertEqual(instance['grants']['GR-maintenance-only']['roles'], ['maintenance'])

    def test_fingerprint_mismatch_and_public_rerecord_preserve_the_failed_transition(self):
        import os
        from do_math import trust_inventory
        from support.engine_cli_conditions import setup_call
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sim = Sim(root / 'sim')
            journey = Journey(sim, root)
            original = deepcopy(journey.state()[1]['lifecycle']['immutable_input'])
            executable = sim.trust_lean
            executable.parent.mkdir(parents=True)
            executable.write_bytes(b'conditional journey external Lean double')
            prelude = executable.parents[1] / 'lib/lean/Init/Prelude.olean'
            prelude.parent.mkdir(parents=True)
            prelude.write_bytes(b'conditional journey synthetic prelude')
            source, _ = trust_inventory.validation_program({'project': None})
            sim.lean.inputs[source.encode('utf-8')] = {}
            command, _ = journey.document('command', {'lean_command': [str(executable)]})
            options = ('--command-file', command, '--records-dir', root / 'records', '--evidence-dir', root / 'evidence')
            trust_file = root / 'trust.json'
            code, recorded = setup_call(sim, '--verify-only', *options, '--trust-file', trust_file)
            self.assertEqual((code, recorded['status']), (0, 'recorded'))
            self.assertEqual(journey.call('trust', '--file', trust_file)['effect'], 'applied')
            query = journey.call('query', '--kind', 'trust-environment', '--limit', '1000')
            env, = [row['record'] for row in query['items']]
            transition, _ = journey.document('transition', {'operation': 'transition', 'env_id': env['id']})
            self.assertEqual(journey.call('trust', '--file', transition)['effect'], 'applied')
            original_record = trust_inventory.read_record(recorded['record_path'])
            stat = prelude.stat()
            os.utime(prelude, ns=(stat.st_atime_ns, stat.st_mtime_ns - 2_000_000_000))
            journey.call('run', '--max-steps', '1')
            failed = deepcopy(journey.state()[2])
            self.assertIsNone(journey.state()[1]['active_trust_environment'])
            self.assertEqual(sim.model.calls, [])
            activation, = [row for row in failed['executions'].values() if row['role'] == 'trust_activate']
            self.assertEqual((activation['status'], activation['outcome']), ('ended', 'execution_incomplete'))
            compile_count = len(sim.lean.checks)
            code, refused = setup_call(sim, '--verify-only', *options)
            self.assertEqual((code, refused['status']), (1, 'rerecord_required'))
            self.assertEqual(refused['record_path'], recorded['record_path'])
            self.assertEqual(len(sim.lean.checks), compile_count)
            next_trust = root / 'rerecorded-trust.json'
            code, rerecorded = setup_call(sim, '--rerecord', *options, '--record', recorded['record_id'],
                                          '--trust-file', next_trust)
            self.assertEqual((code, rerecorded['status']), (0, 'recorded'))
            self.assertEqual(rerecorded['record_id'], recorded['record_id'])
            record = trust_inventory.read_record(rerecorded['record_path'])
            self.assertEqual(record['identity'], original_record['identity'])
            self.assertEqual(record['baselines'][:-1], original_record['baselines'])
            self.assertEqual(len(record['baselines']), 2)
            request = json.loads(next_trust.read_bytes())
            self.assertEqual(request['binding'], rerecorded['binding'])
            self.assertEqual(request['toolchain_record'], env['toolchain_record'])
            sim.restart()
            # A failed transition is terminal. Repeating its original receipt
            # is inert; a new explicit transition checks the same environment.
            terminal = deepcopy(journey.state()[2]['trust_transitions'])
            replay = journey.call('trust', '--file', transition)
            self.assertTrue(replay['replayed'])
            self.assertEqual(journey.state()[2]['trust_transitions'], terminal)
            self.assertEqual(journey.call('trust', '--file', transition,
                                         '--idempotency-key', 'after-public-rerecord')['effect'], 'applied')
            journey.call('run', '--max-steps', '1')
            _, instance, runtime = journey.state()
            self.assertEqual(instance['active_trust_environment'], env['id'])
            self.assertEqual(instance['lifecycle']['immutable_input'], original)
            self.assertEqual(runtime['trust_bindings'][env['id']], request['binding'])
            successor, = [row for row in runtime['executions'].values() if row['id'] not in failed['executions']]
            self.assertEqual(successor['outcome'], 'output_accepted')
            self.assertNotEqual(successor['owner_activity_id'], activation['owner_activity_id'])
            self.assertEqual({key: runtime['trust_transitions'][key] for key in terminal}, terminal)
            self.assertEqual(runtime['executions'][activation['id']], activation)
            self.assertEqual(sim.model.calls, [])

    def test_normal_native_final_public_retry_reuses_the_preserved_response_without_a_new_model(self):
        from support.engine_cli_conditions import native_capture_refused
        from support.scheduling_initial import adopted_sim
        sim = adopted_sim()
        with tempfile.TemporaryDirectory() as directory:
            journey = Journey(sim, Path(directory))
            original = deepcopy(journey.state()[1]['lifecycle']['immutable_input'])
            sim.model.on('intent_interpretation', stage='interpret').reply(
                Answer(lambda output, context: output, mode='standalone', expected_receipt=None))
            # The first turn checks trust; the second runs only the original interpretation.
            journey.call('run', '--max-steps', '1')
            with native_capture_refused(sim) as refusals:
                journey.call('run', '--max-steps', '1')
            self.assertEqual(len(refusals), 1)
            before = deepcopy(journey.state())
            wait, = before[2]['waiting_actions'].values()
            execution = before[2]['executions'][wait['execution_id']]
            self.assertEqual((execution['status'], execution['outcome']), ('ended', 'execution_incomplete'))
            self.assertEqual(execution['capacity']['local_termination'], 'confirmed')
            raw = sim.engine.store.read(execution['result_ref'])
            result = json.loads(raw)
            self.assertEqual(result['collection'], 'provider_evidence_only')
            self.assertEqual((result['status'], result['provider_result_status']), ('failed', 'completed'))
            self.assertEqual(result['execution']['collect']['result'], 'output_collected')
            self.assertEqual(result['execution']['collect']['worker_status']['cli_exit_code'], 0)
            self.assertTrue(result['execution']['collect']['termination_barrier']['confirmed'])
            self.assertEqual(len(sim.model.calls), 1)
            sim.restart()
            request = journey.call('request', '--retry-action', wait['action']['id'], '--request-id', 'native-receive-once')
            self.assertEqual(request['effect'], 'applied')
            after = journey.state()
            self.assertEqual(after[1]['lifecycle']['immutable_input'], original)
            self.assertEqual(sim.engine.store.read(execution['result_ref']), raw)
            self.assertEqual(len(sim.model.calls), 1)
            # This is receipt recovery, so no fresh interpretation may be queued.
            self.assertEqual([row for row in after[2]['queue'] if row.get('continuation_of') == execution['id']], [])
            self.assertEqual(after[2]['executions'][execution['id']]['outcome'], 'output_accepted')
            recovered = deepcopy(after[2]['executions'][execution['id']])
            self.assertEqual(recovered['owner_activity_id'], execution['owner_activity_id'])
            self.assertEqual(recovered['capacity'], execution['capacity'])
            history = [row for row in after[2]['history'] if row.get('kind') == 'native_final_recovery_requested']
            self.assertEqual(len(history), 1)
            self.assertEqual(history[0]['prior_failure'], wait)
            self.assertEqual(history[0]['prior_result_ref'], execution['result_ref'])
            sim.restart()
            replay = journey.call('request', '--retry-action', wait['action']['id'], '--request-id', 'native-receive-once')
            self.assertEqual(replay, {**request, 'replayed': True})
            self.assertEqual(journey.state()[2]['executions'][execution['id']], recovered)
            self.assertEqual(len(sim.model.calls), 1)
            journey.call('run', '--max-steps', '1')
            after_run = journey.state()
            self.assertEqual(after_run[2]['executions'][execution['id']], recovered)
            self.assertEqual(sum(row['role'] == 'intent_interpretation' and row['action'].get('stage') == 'interpret'
                                 for row in sim.model.calls), 1)
            self.assertEqual(len(sim.model.calls), 2)
            self.assertEqual(sim.model.calls[-1]['action']['stage'], 'check')
            self.assertEqual(sum(row.get('kind') == 'native_final_recovery_completed'
                                 for row in after_run[2]['history']), 1)

    def test_initial_output_repairs_reach_one_maintenance_retry_or_a_durable_wait(self):
        from support.model import amend, raw
        from support.scheduling_initial import adopted_sim
        for decision in ('retry', 'wait'):
            with self.subTest(decision=decision), tempfile.TemporaryDirectory() as directory:
                sim = adopted_sim()
                journey = Journey(sim, Path(directory))
                before = deepcopy(journey.state())
                sim.model.on('intent_interpretation', stage='interpret').reply(
                    raw({'not': 'an interpretation'}, expected_receipt='rejected'))
                guidance = 'Return the required interpretation fields' if decision == 'retry' else 'Ask the user to clarify the goal'
                sim.model.on('maintenance').reply(amend(initial_submission_diagnosis={
                    'decision': decision, 'guidance': guidance}))
                result = journey.call('run', '--until-active')
                self.assertEqual(result['operating_summary']['lifecycle'], 'initializing')
                _, instance, runtime = journey.state()
                self.assertEqual(instance['lifecycle']['immutable_input'], before[1]['lifecycle']['immutable_input'])
                self.assertEqual(instance['grants'], before[1]['grants'])
                interpretations = [row for row in sim.model.calls if row['role'] == 'intent_interpretation']
                diagnoses = [row for row in sim.model.calls if row['role'] == 'maintenance']
                self.assertEqual(len(interpretations), 3 if decision == 'retry' else 2)
                self.assertEqual(len(diagnoses), 1)
                first, repaired = interpretations[:2]
                self.assertNotIn('repair_attempt', first['action'])
                self.assertEqual(repaired['action']['repair_attempt'], instance['config']['max_output_repairs'])
                failed = runtime['executions'][repaired['action']['continuation_of']]
                self.assertEqual(failed['action']['id'], first['action']['id'])
                wait, = runtime['waiting_actions'].values()
                self.assertEqual((wait['kind'], wait['next_owner']), ('output_validation', 'maintenance'))
                owner = runtime['activities'][wait['action']['owner_activity_id']]
                self.assertEqual((owner['status'], owner['waiting']['next_owner']), ('waiting', 'maintenance'))
                if decision == 'retry':
                    retried = interpretations[2]['action']
                    self.assertEqual((retried['diagnosis_attempt'], retried['repair_attempt']), (1, 2))
                    self.assertEqual(diagnoses[0]['action']['target'], retried['continuation_of'])
                    self.assertNotIn('diagnosis', wait)
                else:
                    self.assertEqual((wait['reason'], wait['diagnosis']['decision'], wait['diagnosis']['guidance']),
                                     (guidance, 'wait', guidance))
                executions = [row for row in runtime['executions'].values() if row['actor_kind'] == 'ai']
                self.assertEqual(len(executions), len(interpretations) + 1)
                self.assertTrue(all(row['status'] == 'ended' for row in executions))
                self.assertTrue(all(row['capacity']['local_termination'] == 'confirmed' for row in executions))
                artifacts = {row['result_ref']: sim.engine.store.read(row['result_ref']) for row in executions}
                model_calls = len(sim.model.calls)
                sim.restart()
                journey.call('run', '--until-active')
                restarted = journey.state()[2]
                self.assertEqual(restarted['executions'], runtime['executions'])
                self.assertEqual(restarted['waiting_actions'], runtime['waiting_actions'])
                self.assertEqual(len(sim.model.calls), model_calls)
                self.assertEqual({ref: sim.engine.store.read(ref) for ref in artifacts}, artifacts)

    def test_expired_or_revoked_grants_preserve_the_original_work_without_a_model_call(self):
        """Public grant controls and time, with capability evidence refreshed after expiry."""
        self.maxDiff = None
        from do_math.governance import timestamp
        for condition in ('expired', 'revoked'):
            with self.subTest(condition=condition), tempfile.TemporaryDirectory() as directory:
                sim = Sim.activated()
                journey = Journey(sim, Path(directory))
                before = deepcopy(journey.state())
                action = next(row for row in before[2]['queue'] if row['role'] == 'research_preparation')
                calls = len(sim.model.calls)
                if condition == 'expired':
                    # All deadlines come from the public activation's actual grants.
                    expiry = max(timestamp(grant['expires_at']) for grant in before[1]['grants'].values())
                    sim.advance((expiry - sim.clock.wall()).total_seconds() + 1)
                    current = journey.call('status', '--json')
                    journey.decision('current-capability', {'kind': 'initialization', 'operation': 'probe',
                        'config_sha256': current['config_sha256']})
                else:
                    for identifier in before[1]['grants']:
                        journey.decision('revoke-' + identifier, {'kind': 'revoke', 'grant_id': identifier})
                selected = journey.call('select-profile', '--role', action['role'])
                journey.call('run', '--max-steps', '1')
                _, instance, runtime = journey.state()
                self.assertEqual(len(sim.model.calls), calls)
                self.assertEqual(runtime['executions'], before[2]['executions'])
                self.assertEqual(instance['lifecycle']['immutable_input'], before[1]['lifecycle']['immutable_input'])
                self.assertEqual(instance['lifecycle']['state'], 'active')
                pending = [row for row in runtime['queue'] if row['id'] == action['id']]
                self.assertEqual(len(pending), 1)
                waiting, = pending
                periodic = [event for event in runtime['events'] if event['kind'] == 'research_reconsider_due'
                            and event['id'] not in {old['id'] for old in before[2]['events']}]
                self.assertEqual(len(periodic), 1 if condition == 'expired' else 0)
                additions = {}
                if periodic:
                    self.assertEqual(periodic[0]['at'], before[2]['next_research_reconsider_at'])
                    self.assertIsNone(periodic[0]['target'])
                    additions = {'event_refs': [*action['event_refs'], periodic[0]['id']],
                                 'periodic_reconsideration': True}
                self.assertEqual(waiting, {**action, **additions,
                    'actor_kind': selected['profile']['actor_kind'],
                    'model_selection': selected['selection'], 'dispatch_wait': {
                        'kind': 'lifecycle', 'reason': 'research authority: no current grant permits this action'}})
                self.assertNotIn('profile_ref', waiting)
                self.assertEqual(runtime['activities'], before[2]['activities'])
                status = journey.call('status', '--json')
                self.assertEqual(status['operating_summary']['grants'], [
                    {'id': grant['id'], 'status': grant['status'], 'expires_at': grant['expires_at']}
                    for grant in instance['grants'].values()])
                self.assertEqual(set(instance['grants']), set(before[1]['grants']))

    def test_scheduled_start_runs_the_real_research_cli_before_a_user_pause_ends_it(self):
        """In-process schedule/Job ports; actual OS firing remains a T5 requirement."""
        from do_math import cli, formal, scheduled_operator
        sim = Sim.activated()
        pauses, child_commands, scheduler_results, accepted_publications = [], [], [], []
        original_jobs = list(sim.jobs.programs)
        original_backend = sim.ports.git_backend

        class GitBackend:
            requested_pause = False

            def __getattr__(self, name):
                return getattr(original_backend, name)

            def update_ref(self, repository, ref, new, old):
                changed = original_backend.update_ref(repository, ref, new, old)
                if changed and not self.requested_pause and ref == 'refs/heads/do-math/' + sim.instance_id:
                    head, _, runtime = sim.engine.store.load()
                    accepted = [row for row in runtime['executions'].values()
                                if row['role'] == 'research_preparation' and row['status'] == 'ended'
                                and row.get('outcome') == 'output_accepted']
                    if accepted:
                        self.requested_pause = True
                        accepted_publications.append({'snapshot': head, 'executions': deepcopy(accepted)})
                        pauses.append(sim.control('pause', text='인계 실행 확인 뒤 사용자 정지'))
                return changed

        class ResearchProcess:
            def __init__(self, command, options):
                self.command, self.options = list(command), options

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def wait(self):
                child_commands.append(self.command)
                output = StringIO()
                with redirect_stdout(output):
                    code = cli.main(self.command[2:], ports=sim.ports, environment=sim.environment,
                                    host_id=sim.host_id, codex_home=sim.codex_home)
                self.options['stdout'].write(output.getvalue().encode('utf-8'))
                return code

        def engine_job(argv, cwd, env):
            return formal._worker(Path(argv[5]), spawn=lambda command, **options: ResearchProcess(command, options))

        def is_engine_job(argv):
            if argv[1:3] != ['-B', '-c'] or 'do_math.formal import _worker' not in argv[3]:
                return False
            command = json.loads(Path(argv[5]).read_bytes())['command']
            return len(command) > 2 and Path(command[1]).name == 'do_math.py' and command[2] == 'run'

        # Only the external Jobs port implementation changes. Lean commands retain
        # their original worker/spawn path; model commands run their real workers.
        sim.jobs.programs = [(is_engine_job, engine_job), *original_jobs]

        class Scheduler(FakeScheduler):
            def run(self, action, arguments):
                result = super().run(action, arguments)
                if action == 'start-engine':
                    output = StringIO()
                    with redirect_stdout(output):
                        code = scheduled_operator.main(['run-engine', '--repository', arguments['Repository'],
                            '--instance', arguments['Instance'], '--workspace', arguments['Workspace']],
                            ports=sim.ports, environment=sim.environment, host_id=sim.host_id,
                            codex_home=sim.codex_home)
                    if code != 0:
                        raise AssertionError('예약 연구 진입점 실패: ' + output.getvalue())
                    scheduler_results.append(json.loads(output.getvalue()))
                    result['engine']['state'] = 'Ready'
                return result

        sim.ports = replace(sim.ports, scheduler=Scheduler(), git_backend=GitBackend())
        with tempfile.TemporaryDirectory() as directory:
            journey = Journey(sim, Path(directory))
            before = deepcopy(journey.state())
            model_calls = len(sim.model.calls)
            journey.call('operator', 'install')
            self.assertEqual(len(sim.model.calls), model_calls)
            journey.call('operator', 'start')
            self.assertEqual(len(child_commands), 1)
            command, = child_commands
            self.assertEqual(command[2:], ['run', '--repository', str(sim.repository),
                '--instance', sim.instance_id, '--watch'])
            self.assertEqual(len(sim.model.calls), model_calls + 1)
            self.assertEqual(len(pauses), 1)
            self.assertEqual(len(accepted_publications), 1)
            self.assertEqual(len(accepted_publications[0]['executions']), 1)
            result, = scheduler_results
            self.assertEqual((result['outcome'], result['exit_code']), ('completed', 0))
            _, instance, runtime = journey.state()
            self.assertEqual(instance['lifecycle']['immutable_input'], before[1]['lifecycle']['immutable_input'])
            self.assertEqual(instance['lifecycle']['state'], 'paused')
            self.assertEqual(runtime['resume_lifecycle'], 'active')
            self.assertEqual(runtime['status'], 'paused')
            self.assertIn(pauses[0]['request_id'], runtime['processed_controls'])
            attempts = [row for identifier, row in runtime['executions'].items()
                        if identifier not in before[2]['executions']]
            self.assertEqual(len(attempts), 1)
            self.assertEqual((attempts[0]['role'], attempts[0]['status']), ('research_preparation', 'ended'))
            self.assertEqual(attempts[0]['outcome'], 'output_accepted')
            self.assertEqual(attempts[0]['submission_receipt']['state'], 'accepted')
            self.assertTrue(all(job.done and job.closed for job in sim.jobs.launched))
            latest = Path(instance['workspace']) / 'operator/latest-engine.json'
            startup = result.pop('startup')
            self.assertEqual(json.loads((latest.parent / 'startup.json').read_bytes()), startup)
            self.assertEqual(json.loads(latest.read_bytes()), result)

    def test_answer_file_is_interpreted_checked_and_resolves_the_named_initial_question(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sim = initial_sim(root / 'sim', question='어느 정의역인가?')
            journey = Journey(sim, root)
            original = deepcopy(sim.instance['lifecycle']['immutable_input'])
            question = next(q for q in sim.runtime['question_links'] if q['status'] == 'open')
            answer = '자연수 전체입니다.\r\n추가 권한은 부여하지 않습니다.\n'
            path = root / 'answer.txt'
            path.write_bytes(answer.encode('utf-8'))
            grants = deepcopy(sim.instance['grants'])
            receipt = journey.call('input', '--file', path, '--responds-to', question['id'])
            self.assertEqual(receipt['effect'], 'applied')
            _, _, runtime = journey.state()
            self.assertEqual(next(q for q in runtime['question_links'] if q['id'] == question['id'])['status'], 'open')
            source = next(row for row in runtime['inputs'] if row['text'] == answer)
            # 외부 모델 응답만 지정한다. 실제 원문 해석과 독립 검사·적용은 엔진이 수행한다.
            sim.model.rules.clear()
            response = interpreted(lambda context: {
                'kind': 'question_answer', 'text': answer, 'target_ids': [sim.instance_id],
                'resolves_questions': [question['id']]})
            def answer_question(output, context):
                result = response.make(output, context)
                if context['action'].get('stage', 'interpret') == 'interpret':
                    result['import_units'][0]['owner_ref'] = question['id']
                return result
            sim.model.on('intent_interpretation', target=source['id']).reply(Answer(answer_question))
            journey.call('run', '--until-active')
            _, instance, runtime = journey.state()
            bundles = [row for row in runtime['intent_imports'].values() if row['input_ref'] == source['id']]
            self.assertEqual(len(bundles), 1)
            self.assertEqual(bundles[0]['check']['decision'], 'approved')
            queried = journey.call('query', '--kind', 'intent_imports', '--limit', '1000')
            approval_path = root / 'answer-approval.json'
            draft = journey.call('prepare-import-approval', '--snapshot', queried['snapshot'],
                                 '--import-id', bundles[0]['id'], '--output', approval_path)
            self.assertEqual(draft['effect'], 'draft_only')
            self.assertEqual(journey.call('decision', '--file', approval_path)['effect'], 'applied')
            journey.call('run', '--until-active')
            _, instance, runtime = journey.state()
            self.assertEqual(instance['lifecycle']['immutable_input'], original)
            self.assertEqual(instance['grants'], grants)
            resolved = next(q for q in runtime['question_links'] if q['id'] == question['id'])
            self.assertEqual(resolved['status'], 'resolved')
            self.assertEqual(runtime['intent_imports'][bundles[0]['id']]['application']['status'], 'applied')

    def test_operator_hold_blocks_start_and_release_preserves_the_same_instance(self):
        sim = Sim.activated()
        with tempfile.TemporaryDirectory() as directory:
            journey = Journey(sim, Path(directory))
            original = deepcopy(sim.instance['lifecycle']['immutable_input'])
            installed = journey.call('operator', 'install')
            self.assertIsNotNone(installed['operator'])
            observed = journey.call('operator', 'status')
            self.assertEqual(observed, installed)
            held_result = journey.call('operator', 'hold', '--reason', '운전자 점검')
            self.assertEqual(held_result['pause']['effect'], 'applied')
            calls = len(sim.ports.scheduler.calls)
            blocked = journey.call('operator', 'start')
            self.assertEqual(blocked['outcome'], 'held')
            self.assertEqual(sim.ports.scheduler.calls[calls:], [])
            released = journey.call('operator', 'release')
            self.assertEqual(released['resume']['effect'], 'applied')
            self.assertEqual(journey.state()[1]['lifecycle']['immutable_input'], original)
            self.assertEqual(journey.state()[1]['lifecycle']['state'], 'active')

    def test_checked_import_draft_is_inert_and_exact_public_approval_applies_without_new_model(self):
        sim = initial_checked_sim()
        with tempfile.TemporaryDirectory() as directory:
            journey = Journey(sim, Path(directory))
            query = journey.call('query', '--kind', 'intent_imports', '--limit', '1000')
            self.assertEqual(len(query['items']), 1)
            bundle = query['items'][0]['record']
            read = journey.call('read', '--snapshot', query['snapshot'], '--id', bundle['id'])
            self.assertEqual(read['record'], bundle)
            before = deepcopy(journey.state())
            path = Path(directory) / 'approval.json'
            draft = journey.call('prepare-import-approval', '--snapshot', query['snapshot'],
                                 '--import-id', bundle['id'], '--output', path)
            self.assertEqual(draft['effect'], 'draft_only')
            self.assertEqual(journey.state(), before)
            self.assertEqual(json.loads(path.read_bytes()), draft['decision'])
            calls = len(sim.model.calls)
            result = journey.call('decision', '--file', path)
            self.assertEqual(result['effect'], 'applied')
            after = journey.call('query', '--kind', 'intent_imports', '--limit', '1000')
            self.assertEqual(after['items'][0]['record']['application']['status'], 'applied')
            _, instance, runtime = journey.state()
            self.assertEqual(instance['governance_sources'][result['request_id']]['text'], path.read_bytes().decode())
            self.assertEqual(instance['governance_sources'][result['request_id']]['origin'], 'user')
            self.assertEqual(len(sim.model.calls), calls)
            self.assertEqual(runtime['executions'], before[2]['executions'])
