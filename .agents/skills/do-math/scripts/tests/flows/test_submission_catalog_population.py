"""실제 역할 입력의 광고 원소마다 producer 검사하고 그 합집합을 중앙 적용한다."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import traceback
import unittest

from do_math import submission
from do_math.canonical import canonical_json
from support.engine_lifecycle import applied, clear_work
from support.sim import Sim, warm_template
from support.submission_calls import submission_model, submitted
from support.submission_owner_obligations import OwnerIngressAssertions


def setUpModule():
    warm_template()


class CatalogPopulationTests(OwnerIngressAssertions, unittest.TestCase):
    def install_probe(self, sim, roles, *, negative_ready=False, negative_profiles=False):
        """정상 응답 생산자를 한 번만 부르고 고정 입력의 광고를 독립 비교한다."""
        model = submission_model(sim, responder=sim.model.responder)
        seen, failures = {}, []

        def inspect(context, workspace):
            try:
                workspace = Path(workspace)
                fixed = json.loads((workspace / 'input/submission/context.json').read_bytes())
                action = fixed['action']
                key = (action['role'], action.get('stage',
                    'interpret' if action['role'] == 'intent_interpretation' else None),
                    bool(action.get('review_cycle_id')))
                if key in seen:
                    return
                output, contract = model.output(action['role'], context, workspace)
                self.assertEqual((contract.mode, contract.expected_receipt), ('bound', 'accepted'))
                sidecar = workspace / 'activity-extensions.json'
                extensions = json.loads(sidecar.read_bytes()) if sidecar.exists() else {}
                references = [row['value'] for row in fixed['reference_catalog']]
                self.assertEqual(len(references), len(set(references)))
                for source in fixed.get('sources', []):
                    forms = [source['id'], source['name'], source['path'], 'source:' + source['name']]
                    if source.get('local_path'):
                        forms.append(source['local_path'])
                    self.assertEqual(set(forms) - set(references), set(), (key, source))
                draft = workspace / '.scratch/catalog-draft.json'
                draft.parent.mkdir(exist_ok=True)
                if negative_profiles and action['role'] == 'research_preparation':
                    candidates = output['candidates']
                    self.assertTrue(candidates)
                    allowed = fixed['role_profile_refs']['research_work']
                    # 정상 bind_candidates는 registry 순서로 생산한다. 허용 집합의
                    # 표시 순서는 계약이 아니며 중복 수와 각 판본 전체는 보존한다.
                    self.assertCountEqual(candidates[0]['profile_refs'], allowed)
                    registry = {row['id']: row for row in fixed['execution_profiles']}
                    self.assertTrue(allowed)
                    for number, reference in enumerate(candidates[0]['profile_refs']):
                        self.assertEqual(registry[reference['id']]['role'], 'research_work')
                        for field, value in (('id', 'EP-outside'), ('revision', reference['revision'] + 1),
                                             ('sha256', '0' * 64)):
                            bad = deepcopy(output)
                            bad['candidates'][0]['profile_refs'][number][field] = value
                            draft.write_bytes(canonical_json(bad))
                            check = submission.producer_check(workspace, draft, clock=sim.clock)
                            expected = ('submission.output.candidates.*', 'output/candidates/0',
                                        'profile reference is absent or stale')
                            self.assertEqual([(row['rule_id'], row['path'], row['message'])
                                for row in check['issues'] if row['path'] == expected[1]], [expected])
                            self.reject_and_replay(sim, workspace, fixed['control_binding'], bad, extensions,
                                expected, 'profile-' + str(number) + '-' + field)
                    sidecar.write_bytes(canonical_json(extensions))
                if negative_ready and action['role'] == 'research_plan':
                    ready = fixed['ready_task_ids']
                    self.assertTrue(ready)
                    actual = [row['task_id'] for row in output['dispositions']]
                    self.assertEqual(sorted(actual), sorted(ready))
                    rows = output['dispositions']
                    unknown = {**rows[0], 'task_id': 'TK-outside'}
                    cases = [(rows[1:], [rows[0]['task_id']], [], []),
                        ([*rows, unknown], [], ['TK-outside'], []),
                        ([*rows, rows[0]], [], [], [rows[0]['task_id']]),
                        ([unknown, unknown], sorted(ready), ['TK-outside'], ['TK-outside'])]
                    for index, (changed, missing, unexpected, duplicate) in enumerate(cases):
                        bad = {**output, 'dispositions': changed}
                        draft.write_bytes(canonical_json(bad))
                        check = submission.producer_check(workspace, draft, clock=sim.clock)
                        reason = ('plan must dispose every derived-ready task exactly once: '
                            f'missing={missing}; unexpected={unexpected}; duplicate={duplicate}')
                        self.assertEqual([(row['rule_id'], row['path'], row['message'])
                            for row in check['issues'] if row['rule_id'] == 'submission.output'],
                            [('submission.output', 'output', reason)])
                        self.reject_and_replay(sim, workspace, fixed['control_binding'], bad, extensions,
                            ('submission.output', 'output', reason), 'ready-' + str(index))
                    sidecar.write_bytes(canonical_json(extensions))
                for reference in references:
                    current = deepcopy(output)
                    current['used_sources'] = list(dict.fromkeys([*output['used_sources'], reference]))
                    draft.write_bytes(canonical_json(current))
                    check = submission.producer_check(workspace, draft, clock=sim.clock)
                    self.assertEqual((check['passed'], check['issues']), (True, []), (key, reference))
                output['used_sources'] = list(dict.fromkeys([*output['used_sources'], *references]))
                seen[key] = {'execution_id': fixed['execution_id'], 'references': output['used_sources']}
                model.on(action['role'], execution_id=fixed['execution_id']).reply(
                    submitted(output, extensions=extensions))
            except Exception:
                failures.append(traceback.format_exc())
                raise

        for role in roles:
            model.before(role, inspect)
        return seen, failures

    def test_ready_population_missing_extra_duplicate_and_mixed_requests_are_rejected_once(self):
        """실제 비빈 ready 광고의 누락·과잉·중복을 양쪽 검사와 소비에서 구별한다."""
        sim = Sim.activated()
        seen, failures = self.install_probe(sim, {'research_plan'}, negative_ready=True)
        self.assert_catalog_applied(sim, {'research_plan'}, seen, failures)

    def test_every_advertised_work_profile_edition_is_preserved_and_stale_fields_are_rejected(self):
        """입력이 허용한 작업 프로필 전건과 각 ID·판본·해시 경계를 양쪽에서 검사한다."""
        sim = Sim.activated()
        seen, failures = self.install_probe(sim, {'research_preparation'}, negative_profiles=True)
        self.assert_catalog_applied(sim, {'research_preparation'}, seen, failures)

    def assert_catalog_applied(self, sim, roles, seen, failures, *, stages=None):
        def done(state):
            self.assertEqual(failures, [], '\n'.join(failures))
            return (stages is None or stages <= {key[1] for key in seen}) and roles <= {key[0] for key in seen} and all(
                state.runtime['executions'][row['execution_id']]['status'] == 'ended' for row in seen.values())
        sim.run_until(done, max_steps=20)
        for key, row in seen.items():
            execution = sim.runtime['executions'][row['execution_id']]
            self.assertEqual(execution['outcome'], 'output_accepted', (key, execution.get('integration_result')))
            output = json.loads(sim.engine.store.read(execution['submission_intent']['output_ref'], sim.engine.head))
            self.assertEqual(output['used_sources'], row['references'])

    def test_live_preparation_review_plan_work_and_maintenance_catalogs_are_applied(self):
        """공개 등록 source와 비빈 과제 상태를 실제 역할 호출에서 검사한다."""
        sim = Sim.activated()
        source = sim.root / '광고-원문.txt'
        source.write_text('공개로 도착한 정확한 원문', encoding='utf-8')
        applied(sim, 'source', config={'path': str(source)})
        roles = {'research_preparation', 'task_contract_review', 'research_plan', 'research_work', 'maintenance'}
        seen, failures = self.install_probe(sim, roles)
        sim.engine._enqueue('maintenance')
        sim.engine._save()
        self.assert_catalog_applied(sim, roles, seen, failures)

    def test_initial_interpretation_and_check_catalogs_are_applied(self):
        with tempfile.TemporaryDirectory() as directory:
            sim = Sim(Path(directory))
            seen, failures = self.install_probe(sim, {'intent_interpretation'})
            sim.activate()
            self.assert_catalog_applied(sim, {'intent_interpretation'}, seen, failures)
            self.assertEqual({key[1] for key in seen}, {'interpret', 'check'})

    def test_active_interpretation_and_check_catalogs_are_applied(self):
        sim = Sim.activated()
        clear_work(sim)
        seen, failures = self.install_probe(sim, {'intent_interpretation'})
        sim.control('input', text='현재 연구 범위와 승인된 판단 기준을 다시 검토해 달라.')
        self.assert_catalog_applied(sim, {'intent_interpretation'}, seen, failures, stages={'interpret', 'check'})
        self.assertEqual({key[1] for key in seen}, {'interpret', 'check'})

    def test_goal_audit_catalog_is_accepted_by_workspace_and_central_application(self):
        from support.review_sim import reviewed_sim
        sim = reviewed_sim()
        seen, failures = self.install_probe(sim, {'goal_audit'})
        sim.engine._enqueue('goal_audit')
        sim.engine._save()
        self.assert_catalog_applied(sim, {'goal_audit'}, seen, failures)

    def test_completed_task_outside_comparison_remains_an_advertised_accepted_reference(self):
        """실제 계획이 완료한 과제를 다음 계획이 인용해도 다시 평가하거나 소거하지 않는다."""
        from support.scheduling_parallel import ready_work_sim
        sim = ready_work_sim(1, max_output_repairs=0)
        task_id, = sim.runtime['tasks']
        sim.run_until(lambda s: s.runtime['tasks'][task_id]['status'] == 'completed', max_steps=8)
        before = deepcopy(sim.runtime['tasks'][task_id])
        clear_work(sim)
        seen, failures = self.install_probe(sim, {'research_plan'})
        sim.engine._enqueue('research_plan', reason='완료 과제를 인용하여 남은 범위를 검토한다')
        sim.engine._save()
        self.assert_catalog_applied(sim, {'research_plan'}, seen, failures)
        self.assertTrue(all(task_id in row['references'] for row in seen.values()))
        self.assertEqual(sim.runtime['tasks'][task_id], before)

    def test_fixed_review_and_investigation_catalogs_are_applied(self):
        from support.review_research import research_sim, InvestigationResponder
        sim = research_sim()
        sim.model.responder = InvestigationResponder()
        roles = {'identity_review', 'supplemental_research'}
        seen, failures = self.install_probe(sim, roles)
        self.assert_catalog_applied(sim, roles, seen, failures)
        self.assertEqual(sim.model.responder.failures, [])
