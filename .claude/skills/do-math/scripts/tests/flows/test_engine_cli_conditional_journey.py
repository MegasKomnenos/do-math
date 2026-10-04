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
                    'actor_kind': selected['profile']['actor_kind'], 'profile_ref': selected['selection']['profile_ref'],
                    'model_selection': selected['selection'], 'dispatch_wait': {
                        'kind': 'lifecycle', 'reason': 'research authority: no current grant permits this action'}})
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
