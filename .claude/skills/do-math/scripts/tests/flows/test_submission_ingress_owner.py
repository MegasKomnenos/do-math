"""2-A의 실제 owner: 앞 검사를 우회한 반려·재전달 뒤 정상 제출.

실제 runner/worker/Repository를 유지한다. 여러 요청의 소비까지 관찰하므로
flows에 둔다. 각 영수증 대기는 100 owner 차례, 역할 흐름은 명시한 8~30 step 이내다.
"""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest


from do_math import submission
from do_math.canonical import canonical_json
from support.engine_lifecycle import applied
from support.provider_probes import ObservedCalls
from support.record_builders import two_observation_output
from support.scheduling_parallel import ready_work_sim
from support.sim import Sim, warm_template
from support.ingress import NOT_TEXTS, PATHS
from support.submission_calls import submission_model, submitted
from support.submission_owner_obligations import OwnerIngressAssertions
from support.known_defects import known_defect
from support.submission_obligations import (
    ROOT_REFERENCES, extension_ingresses, item_shapes, maintenance_output,
)


def setUpModule():
    warm_template()
    ready_work_sim(1, max_output_repairs=0)


class OwnerIngressTests(OwnerIngressAssertions, unittest.TestCase):


    def test_initial_interpretation_and_check_families_are_consumed_before_activation(self):
        """초기 공개 활성화의 해석·독립 검토를 각각 실제 소유자에서 검사한다."""
        with tempfile.TemporaryDirectory() as directory:
            sim = Sim(Path(directory))
            seen, failures = self.install_family_probe(sim, {'intent_interpretation'})
            sim.activate()
            self.await_family_probes(sim, {'intent_interpretation'}, seen, failures)
            self.assert_family_accepted(sim, seen)
            self.assertEqual({key[1] for key in seen}, {'interpret', 'check'})
            self.assertEqual(sim.instance['lifecycle']['state'], 'active')

    def test_review_seats_and_goal_audit_families_preserve_normal_progress(self):
        """실제 정리의 검토 좌석과 목표 감사에서 반려 뒤 정상 판정을 적용한다."""
        from support.review_sim import opened_sim, cycle_of
        sim = opened_sim()
        roles = {'identity_review', 'goal_audit'}
        seen, failures = self.install_family_probe(sim, roles)
        sim.run_until(lambda s: bool(failures) or cycle_of(s)['status'] != 'working', max_steps=12)
        self.assertEqual(failures, [], '\n'.join(failures))
        self.assertEqual(cycle_of(sim)['decision'], 'match')
        sim.engine.runtime['queue'] = [{'id': 'AC-submission-goal', 'role': 'goal_audit'}]
        sim.engine._save()
        self.await_family_probes(sim, roles, seen, failures)
        self.assert_family_accepted(sim, seen)
        self.assertIn(('identity_review', 'scope', True, False, False), seen)
        self.assertIn(('identity_review', 'initial', True, False, False), seen)

    def test_fixed_question_investigator_has_no_extension_family_and_accepts_normal_answer(self):
        """고정 질문 조사에는 확장이 없으며 실제 고정 원문 답을 중앙이 수락한다."""
        from support.review_research import research_sim, InvestigationResponder
        sim = research_sim()
        sim.model.responder = InvestigationResponder()
        roles = {'identity_review', 'supplemental_research'}
        seen, failures = self.install_family_probe(sim, roles)
        self.await_family_probes(sim, roles, seen, failures, max_steps=30)
        self.assert_family_accepted(sim, seen)
        research = [row for key, row in seen.items() if key[0] == 'supplemental_research']
        self.assertTrue(research)
        self.assertEqual([row['families'] for row in research], [[]] * len(research))


    def test_preparation_review_plan_and_work_families_reach_the_actual_owner(self):
        """실제 준비→검토→계획→연구의 가족 전건과 뒤 정상 처리를 확인한다.

        필수·열거·고정값 전건의 반려와 재전달을 유지하여 묶음 실측은 101.328초다.
        flows의 60초 예산 초과를 보고하며 입력이나 단언을 줄이지 않는다.
        """
        sim = Sim.activated()
        roles = {'research_preparation', 'task_contract_review', 'research_plan', 'research_work'}
        seen, failures = self.install_family_probe(sim, roles)
        def finished(state):
            self.assertEqual(failures, [], '\n'.join(failures))
            return roles <= {key[0] for key in seen} and all(
                state.runtime['executions'][row['execution_id']]['status'] == 'ended'
                for row in seen.values())
        sim.run_until(finished, max_steps=16)
        self.assertEqual({key[0] for key in seen}, roles)
        for key, row in seen.items():
            execution = sim.runtime['executions'][row['execution_id']]
            self.assertEqual(execution['outcome'], 'output_accepted', key)
            self.assertEqual(execution['integration_result']['status'], 'accepted', key)


    def test_workspace_roots_are_consumed_once_before_a_valid_maintenance_submission(self):
        """루트·빈·상위·드라이브 경로와 비문자 JSON 참조의 정확 중앙 반려."""
        sim = Sim.activated()
        sim.engine.runtime['queue'] = [{'id': 'AC-submission-root', 'role': 'maintenance'}]
        sim.engine._save()
        model = submission_model(sim)
        seen = []

        def malformed(context, workspace):
            fixed = json.loads((Path(workspace) / 'input/submission/context.json').read_bytes())
            seen.append(fixed['execution_id'])
            cases = [(reference, 'submission.output.used_sources.*',
                      'unsafe relative path: ' + reference.removeprefix('workspace:'))
                     for reference in ROOT_REFERENCES]
            for name in PATHS:
                # used_sources는 문자열 목록이다. 경로의 비어 있음은 경로 수신이 검사한다.
                cases.append((name, 'submission.output.used_sources.*',
                    'path must be a nonempty relative POSIX path' if name == '' or ':' in name else
                    'unsafe relative path: ' + name))
                cases.append(('workspace:' + name, 'submission.output.used_sources.*',
                    'path must be a nonempty relative POSIX path' if name == '' or ':' in name else
                    'unsafe relative path: ' + name))
            cases.extend((value, 'schema.type', f"{value!r} is not of type 'string'")
                         for value in NOT_TEXTS)
            for index, (reference, rule, message) in enumerate(cases):
                self.reject_and_replay(sim, workspace, fixed['control_binding'],
                    {**maintenance_output(), 'used_sources': [reference]}, {},
                    [(rule, 'output/used_sources/0', message)], index)
            seen.append(len(cases))
            (Path(workspace) / 'activity-extensions.json').write_bytes(b'{}')

        model.before('maintenance', malformed)
        model.on('maintenance').reply(submitted(maintenance_output()))
        with ObservedCalls(seal=submission.seal_submission, producer=submission.producer_check) as calls:
            sim.run_until(lambda s: bool(seen) and s.runtime['executions'][seen[0]]['status'] == 'ended', max_steps=8)
        # Each malformed case is checked by the helper; the normal submission adds none.
        self.assertEqual(calls.count('producer', caller=self.reject_and_replay.__module__), seen[1])
        self.assertEqual(calls.count('producer'), seen[1])
        execution = sim.runtime['executions'][seen[0]]
        self.assertEqual(execution['outcome'], 'output_accepted', execution.get('error'))
        self.assertEqual(calls.count('seal'), seen[1] + 1)
        stored_raw = sim.engine.store.read(execution['submission_intent']['output_ref'], sim.engine.head)
        stored = json.loads(stored_raw)
        self.assertEqual({key: value for key, value in stored.items() if key != 'integration_bundles'},
                         maintenance_output())
        sim.restart()
        self.assertEqual(sim.runtime['executions'][seen[0]]['outcome'], 'output_accepted')
        self.assertEqual(sim.engine.store.read(execution['submission_intent']['output_ref'], sim.engine.head),
                         stored_raw)

    def test_maintenance_extension_table_is_consumed_before_a_valid_submission(self):
        sim = Sim.activated()
        sim.engine.runtime['queue'] = [{'id': 'AC-submission-family', 'role': 'maintenance'}]
        sim.engine._save()
        model = submission_model(sim)
        rows = [row for row in extension_ingresses() if row.action == {'role': 'maintenance'}]
        seen = []

        def malformed(context, workspace):
            fixed = json.loads((Path(workspace) / 'input/submission/context.json').read_bytes())
            seen.append(fixed['execution_id'])
            for index, (row, (_, value)) in enumerate((r, item) for r in rows for item in item_shapes()):
                self.reject_and_replay(sim, workspace, fixed['control_binding'], maintenance_output(),
                    {row.family: [value]}, [('schema.type', 'activity-extensions.json/' + row.family + '/0',
                                           f"{value!r} is not of type 'object'")], index)
            (Path(workspace) / 'activity-extensions.json').write_bytes(b'{}')

        model.before('maintenance', malformed)
        model.on('maintenance').reply(submitted(maintenance_output()))
        with ObservedCalls(seal=submission.seal_submission, producer=submission.producer_check) as calls:
            sim.run_until(lambda s: bool(seen) and s.runtime['executions'][seen[0]]['status'] == 'ended', max_steps=8)
        # The rejection helper checks each malformed case at both boundaries.
        expected_producer_calls = len(rows) * len(item_shapes())
        self.assertEqual(calls.count('producer', caller=self.reject_and_replay.__module__), expected_producer_calls)
        self.assertEqual(calls.count('producer'), expected_producer_calls)
        self.assertEqual(calls.count('seal'), len(rows) * len(item_shapes()) + 1)
        self.assertEqual(sim.runtime['executions'][seen[0]]['outcome'], 'output_accepted')

    def test_metadata_nonobjects_preserve_the_research_envelope_and_next_output(self):
        sim = ready_work_sim(1, max_output_repairs=0)
        model = submission_model(sim)
        seen = []
        good = two_observation_output()
        good.pop('integration_bundles')

        def malformed(context, workspace):
            fixed = json.loads((Path(workspace) / 'input/submission/context.json').read_bytes())
            seen.append(fixed['execution_id'])
            for index, (_, value) in enumerate(item_shapes()):
                self.reject_and_replay(sim, workspace, fixed['control_binding'], good,
                    {'knowledge_metadata': [value]},
                    [('schema.type', 'activity-extensions.json/knowledge_metadata/0',
                     f"{value!r} is not of type 'object'")], index)
            (Path(workspace) / 'activity-extensions.json').write_bytes(b'{}')

        model.before('research_work', malformed)
        model.on('research_work').reply(submitted(good))
        prior = set(sim.instance['knowledge'])
        sim.run_until(lambda s: bool(seen) and s.runtime['executions'][seen[0]]['status'] == 'ended', max_steps=8)
        self.assertEqual(sim.runtime['executions'][seen[0]]['outcome'], 'output_accepted')
        added = [row for key, row in sim.instance['knowledge'].items() if key not in prior]
        self.assertEqual(sorted(row['title'] for row in added), ['A', 'B'])
        sim.restart()
        self.assertEqual(sorted(row['title'] for key, row in sim.instance['knowledge'].items() if key not in prior), ['A', 'B'])

    def test_metadata_returns_only_its_bundle_and_preserves_the_independent_bundle(self):
        sim = ready_work_sim(1, max_output_repairs=0)
        model = submission_model(sim)
        bad = two_observation_output()
        bad['integration_bundles'][0]['members'].append('activity-extensions.json/knowledge_metadata/0')
        seen = []
        model.before('research_work', lambda context, workspace: seen.append(context['execution_id']))
        model.on('research_work').reply(submitted(bad, extensions={'knowledge_metadata': [None]}))
        before = set(sim.instance['knowledge'])
        sim.run_until(lambda s: bool(seen) and s.runtime['executions'][seen[0]]['status'] == 'ended', max_steps=8)
        execution = sim.runtime['executions'][seen[0]]
        self.assertEqual(execution['submission_receipt']['state'], 'accepted')
        self.assertEqual(execution['integration_result']['status'], 'partial')
        self.assertEqual([(row['integration_id'], row['status']) for row in execution['integration_result']['bundles']],
                         [('IN-A', 'returned'), ('IN-B', 'accepted')])
        self.assertEqual(execution['integration_result']['retry_bundle_ids'], ['IN-A'])
        self.assertEqual([(row['rule_id'], row['path'], row['integration_id']) for row in execution['integration_result']['issues']],
                         [('schema.type', 'activity-extensions.json/knowledge_metadata/0', 'IN-A')])
        added = {key: value for key, value in sim.instance['knowledge'].items() if key not in before}
        self.assertEqual([value['title'] for value in added.values()], ['B'])
        sim.restart()
        self.assertEqual({key: value for key, value in sim.instance['knowledge'].items() if key not in before}, added)

    def test_partial_metadata_retry_does_not_apply_the_accepted_bundle_twice(self):
        """실제 소유자의 복구 호출이 반려 묶음만 수리하고 이미 수락한 지식을 보존한다."""
        sim = ready_work_sim(1, max_output_repairs=1)
        model = submission_model(sim)
        output = two_observation_output()
        output['integration_bundles'][0]['members'].append('activity-extensions.json/knowledge_metadata/0')
        def repaired(context):
            return {**deepcopy(output), 'repair_responses': [
                {'issue_id': row['issue_id'], 'disposition': 'resolved', 'reason': '중첩 metadata 원소를 정상 제목 객체로 고쳤다.'}
                for row in context['submission_failures']]}
        model.on('research_work').reply(submitted(output, extensions={'knowledge_metadata': [None]})).reply(
            submitted(repaired, extensions={'knowledge_metadata': [{'title': 'A'}]}))
        seen, accepted = [], {}
        before = set(sim.instance['knowledge'])
        def observe(context, workspace):
            seen.append(context['execution_id'])
            if len(seen) == 2:
                accepted.update({key: deepcopy(value) for key, value in sim.instance['knowledge'].items()
                                 if key not in before})
                self.assertEqual([row['title'] for row in accepted.values()], ['B'])
                self.assertIn('IN-B', context['accepted_integration_ids'])
        model.before('research_work', observe)
        sim.run_until(lambda s: len(seen) == 2 and s.runtime['executions'][seen[1]]['status'] == 'ended', max_steps=10)
        self.assertEqual(sim.runtime['executions'][seen[0]]['integration_result']['status'], 'partial')
        self.assertEqual(sim.runtime['executions'][seen[1]]['outcome'], 'output_accepted',
                         sim.runtime['executions'][seen[1]].get('integration_result'))
        self.assertEqual([(row['integration_id'], row['status']) for row in
            sim.runtime['executions'][seen[1]]['integration_result']['bundles']],
            [('IN-A', 'accepted'), ('IN-B', 'already_accepted')])
        self.assertEqual({key: sim.instance['knowledge'][key] for key in accepted}, accepted)
        added = {key: row for key, row in sim.instance['knowledge'].items() if key not in before}
        self.assertEqual(sorted(row['title'] for row in added.values()), ['A', 'B'])
        sim.restart()
        self.assertEqual({key: row for key, row in sim.instance['knowledge'].items() if key not in before}, added)

    def test_actual_maintenance_catalog_is_accepted_by_producer_and_central_application(self):
        sim = Sim.activated()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'submission-source.txt'
            source.write_text('정확히 제공한 원 자료', encoding='utf-8')
            applied(sim, 'source', config={'path': str(source)})
            sim.engine.runtime['queue'] = [{'id': 'AC-submission-catalog', 'role': 'maintenance'}]
            sim.engine._save()
            model = submission_model(sim)
            selected, seen = [], []

            def producer(context, workspace):
                workspace = Path(workspace)
                fixed = json.loads((workspace / 'input/submission/context.json').read_bytes())
                seen.append(fixed['execution_id'])
                selected.extend(row['value'] for row in fixed['reference_catalog'])
                source_row, = [row for row in fixed['sources'] if row['name'] == source.name]
                forms = [source_row['id'], source_row['name'], 'source:' + source_row['name'], source_row['path']]
                if source_row.get('local_path'):
                    forms.append(source_row['local_path'])
                self.assertEqual(set(forms) - set(selected), set())
                self.assertEqual(len(selected), len(set(selected)))
                for reference in selected:
                    draft = workspace / 'advertised-draft.json'
                    draft.write_bytes(canonical_json({**maintenance_output(), 'used_sources': [reference]}))
                    check = submission.producer_check(workspace, draft, clock=sim.clock)
                    self.assertEqual((check['passed'], check['issues']), (True, []), reference)

            model.before('maintenance', producer)
            model.on('maintenance').reply(submitted(lambda context: {**maintenance_output(), 'used_sources': list(selected)}))
            sim.run_until(lambda s: bool(seen) and s.runtime['executions'][seen[0]]['status'] == 'ended', max_steps=8)
        execution = sim.runtime['executions'][seen[0]]
        self.assertEqual(execution['outcome'], 'output_accepted')
        self.assertEqual((execution['integration_result']['status'], execution['integration_result']['issues']), ('accepted', []))
        output = json.loads(sim.engine.store.read(execution['submission_intent']['output_ref'], sim.engine.head))
        self.assertEqual(output['used_sources'], selected)
        self.assertGreater(len(selected), 0)


class OperationalIngressDefectTests(OwnerIngressAssertions, unittest.TestCase):
    def setUp(self):
        """표시 밖에서 정상 검사·중앙 봉인과 가족 전건의 소비를 확인한다."""
        from support.submission_calls import failed
        self.sim = ready_work_sim(1, max_output_repairs=0)
        self.seen, failures = self.install_family_probe(self.sim, {'operational_review'})
        self.sim.model.on('research_work').reply(failed('제출 의무용 공급자 실패'))
        self.await_family_probes(self.sim, {'operational_review'}, self.seen, failures)
        for row in self.seen.values():
            execution = self.sim.runtime['executions'][row['execution_id']]
            self.assertEqual(execution['submission_receipt']['state'], 'accepted')
            check = json.loads(self.sim.engine.store.read(execution['submission_intent']['check_ref'], self.sim.engine.head))
            self.assertEqual((check['passed'], check['issues']), (True, []))

    def test_valid_user_decision_is_applied_after_rejected_extensions(self):
        self.assert_family_accepted(self.sim, self.seen)
