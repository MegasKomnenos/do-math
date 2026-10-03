"""역할 이름만으로 구분되지 않는 준비·보충 조사 국면의 실제 입구 모집단."""
import unittest
from do_math.canonical import canonical_json

from support.academic_scenes import assessment_sim, rule_prepared
from support.engine_lifecycle import applied, clear_work
from support.scheduling_parallel import ready_work_sim
from support.submission_owner_obligations import OwnerIngressAssertions


class PhasePopulationTests(OwnerIngressAssertions, unittest.TestCase):
    def test_designated_impact_review_consumes_extensions_before_its_normal_judgment(self):
        """실제 영향 검토 요청의 지정 판정과 보통 유지보수를 구분한다."""
        from support.review_sim import impact_sim, impact_review_answer
        sim = impact_sim()
        seen, failures = self.install_family_probe(sim, {'maintenance'})
        sim.model.on('maintenance', stage='impact_review').reply(impact_review_answer())
        self.await_family_probes(sim, {'maintenance'}, seen, failures)
        self.assert_family_accepted(sim, seen)
        self.assertEqual({key[1] for key in seen}, {'impact_review'})

    def test_live_operational_basis_and_extension_families_reach_the_receiver(self):
        """실제 관찰 발동의 근거 전건을 검사하고 중앙 계속 처분까지 확인한다."""
        from do_math.observations import ObservationTracker, tracker_config
        from support.observation_inputs import observation_rule
        from support.provider_live import batch, running_execution
        from support.model import Answer
        from support.sim import Sim
        sim = Sim.activated()
        clear_work(sim)
        workspace = running_execution(sim, 'EX-submission-live', 'research_work', bind=True)
        (workspace / 'argument.txt').write_text('자연수 영역의 덧셈 항등식을 검토했다.', encoding='utf-8')
        (workspace / 'checkpoint.json').write_bytes(canonical_json({
            'current_claim': '자연수에 0을 더해도 값은 같다.', 'evidence_paths': ['argument.txt'],
            'attempts': ['정의 확인'], 'remaining_work': ['결론 작성'], 'next_step': '결론 작성',
            'progress_state': 'working', 'counters': {'attempts': 1}}))
        profile = sim.instance['execution_profiles'][sim.instance['role_profile_refs']['research_work'][0]['id']]
        config = tracker_config(profile, initial_self_check_rules=[observation_rule()])
        tracker = ObservationTracker('EX-submission-live', workspace, config, time_port=sim.clock)
        stream = workspace.parent / 'evidence/stdout.jsonl'
        first = batch(sim, [{'type': 'item.started', 'item': {'type': 'command_execution', 'id': 'observed-tool'}}], stream)
        sim.engine._observe_running('EX-submission-live', tracker, first)
        sim.advance(config['tool_review_window_seconds'] + 1)
        sim.engine._observe_running('EX-submission-live', tracker, batch(sim, [], stream, start=first.end_offset))
        seen, failures = self.install_family_probe(sim, {'operational_review'})
        sim.model.on('operational_review').reply(Answer(lambda output, context: {**output, 'disposition': {
            'kind': 'continue', 'basis_refs': [context['action']['target']], 'next_owner': 'research_work',
            'reason': '검토한 checkpoint와 관찰에 따라 배정 연구를 계속한다.', 'next_review': None}}))
        self.await_family_probes(sim, {'operational_review'}, seen, failures)
        self.assert_family_accepted(sim, seen)
        records = [row for row in sim.runtime['operational_dispositions'].values()
                   if row['execution_id'] in {item['execution_id'] for item in seen.values()}]
        self.assertEqual([row['disposition']['kind'] for row in records], ['continue'])
        self.assertIn('operational_continuation', sim.runtime['executions']['EX-submission-live'])

    def test_assessment_rule_and_combined_preparations_consume_each_advertised_family(self):
        """비빈 대상의 평가 전용·규칙 전용·결합 준비를 실제 저장소에 적용한다."""
        for mode in ('assessment', 'combined', 'rules'):
            with self.subTest(mode=mode):
                sim = rule_prepared() if mode == 'combined' else assessment_sim()
                if mode == 'rules':
                    # 첫 정상 평가 생산자가 model_assessment를 채운 뒤,
                    # 독립 입력인 규칙만 없는 상태를 실제 준비 판정에 준다.
                    sim.run_until(lambda s: all(task.get('model_assessment')
                        for task in s.runtime['tasks'].values()), max_steps=4)
                    sim.engine.runtime['queue'] = []
                    for task in sim.engine.runtime['tasks'].values():
                        task['initial_observation_rules'] = []
                    sim.engine._refresh_readiness()
                    sim.engine._save()
                seen, failures = self.install_family_probe(sim, {'research_preparation'})
                self.await_family_probes(sim, {'research_preparation'}, seen, failures)
                self.assert_family_accepted(sim, seen)
                expected = {'assessment': (True, False), 'combined': (True, True), 'rules': (False, True)}[mode]
                self.assertEqual({key[3:] for key in seen}, {expected})
                for task in sim.runtime['tasks'].values():
                    self.assertTrue(task['model_assessment'])
                    self.assertTrue(task['initial_observation_rules'])

    def test_task_supplemental_research_families_are_not_fixed_question_families(self):
        from support.planning_owner import owner_sim
        sim = owner_sim()
        target, = sim.runtime['tasks']
        clear_work(sim)
        applied(sim, 'request', config={'role': 'supplemental_research', 'target': target},
                text='기존 과제의 보충 조사를 요청한다')
        sim.engine.runtime['queue'] = [row for row in sim.runtime['queue'] if row['role'] == 'supplemental_research']
        sim.engine._save()
        seen, failures = self.install_family_probe(sim, {'supplemental_research'})
        from support.model import amend
        sim.model.on('supplemental_research').reply(amend(
            report='배정 과제의 원문 범위를 검토했으며 추가 지식 없이 미해결 내용을 보존한다.'))
        self.await_family_probes(sim, {'supplemental_research'}, seen, failures)
        self.assert_family_accepted(sim, seen)
        self.assertTrue(all(row['families'] for row in seen.values()))
        self.assertEqual({key[2] for key in seen}, {False})
